from __future__ import absolute_import, division, print_function

import logging
from collections import defaultdict

from ..model import GeoBox
from ..utils import check_intersect
from .query import Query, query_group_by
from .core import Datacube, get_measurements, get_bounds

_LOG = logging.getLogger(__name__)


class GridWorkflow(object):
    """
    GridWorkflow deals with cell- and tile-based processing using a grid defining a projection and resolution.
    """
    def __init__(self, index, grid_spec=None, product=None):
        """
        Create a grid workflow tool.

        Either grid_spec or product must be supplied.

        :param Index index: The database index to use.
        :param GridSpec grid_spec: The grid projection and resolution
        :param str product: The name of an existing product, if no grid_spec is supplied.
        """
        self.index = index
        if grid_spec is None:
            product = self.index.products.get_by_name(product)
            grid_spec = product and product.grid_spec
        self.grid_spec = grid_spec

    def cell_observations(self, cell_index=None, geopolygon=None, **indexers):
        """
        List datasets, grouped by cell.

        :param (int,int) cell_index: The cell index. E.g. (14, -40)
        :param indexers: Query to match the datasets, see :py:class:`datacube.api.query.Query`
        :return: Datsets grouped by cell index
        :rtype: dict[(int,int), list[:py:class:`datacube.model.Dataset`]]

        .. seealso::
            :meth:`datacube.Datacube.product_observations`

            :py:class:`datacube.api.query.Query`
        """
        if cell_index:
            assert isinstance(cell_index, tuple)
            assert len(cell_index) == 2
            geobox = GeoBox.from_grid_spec(self.grid_spec, cell_index)
            geopolygon = geobox.extent
        query = Query(index=self.index, geopolygon=geopolygon, **indexers)

        if not query.product:
            raise RuntimeError('must specify a product')

        observations = self.index.datasets.search_eager(**query.search_terms)
        if not observations:
            return {}

        if cell_index:
            tile_iter = [(cell_index, geobox)]
        else:
            bounds_geopolygon = get_bounds(observations, self.grid_spec.crs)
            tile_iter = self.grid_spec.tiles(bounds_geopolygon.boundingbox)

        tiles = {}
        for tile_index, tile_geobox in tile_iter:
            tile_geopolygon = tile_geobox.extent
            datasets = [dataset for dataset in observations
                        if check_intersect(tile_geopolygon, dataset.extent.to_crs(self.grid_spec.crs))]
            tiles[tile_index] = {
                'datasets': datasets,
                'geobox': tile_geobox
            }
        return tiles

    @staticmethod
    def cell_sources(observations, group_by):
        """
        Group observations into sources

        :param observations: datasets grouped by cell index, like from :meth:`datacube.GridWorkflow.cell_observations`
        :param str group_by: grouping method, one of "time", "solar_day"
        :return: sources grouped by cell index
        :rtype: dict[(int,int), :py:class:`xarray.DataArray`]

        .. seealso::
            :meth:`load`

            :meth:`datacube.Datacube.product_sources`
        """
        stack = defaultdict(dict)
        for cell_index, observation in observations.items():
            sources = Datacube.product_sources(observation['datasets'],
                                               group_func=group_by.group_by_func,
                                               dimension=group_by.dimension,
                                               units=group_by.units)
            stack[cell_index] = {
                'sources': sources,
                'geobox': observation['geobox']
            }
        return stack

    @staticmethod
    def tile_sources(observations, group_by):
        """
        Split observations into tiles and group into sources

        :param observations: datasets grouped by cell index, like from :meth:`datacube.GridWorkflow.cell_observations`
        :param str group_by: grouping method, one of "time", "solar_day"
        :return: sources grouped by cell index and time
        :rtype: dict[tuple(int, int, numpy.datetime64), :py:class:`xarray.DataArray`]

        .. seealso::
            :meth:`load`

            :meth:`datacube.Datacube.product_sources`
        """
        stack = defaultdict(dict)
        for cell_index, observation in observations.items():
            sources = Datacube.product_sources(observation['datasets'],
                                               group_func=group_by.group_by_func,
                                               dimension=group_by.dimension,
                                               units=group_by.units)
            for tile_index in sources[group_by.dimension].values:
                stack[cell_index + (tile_index,)] = {
                    'sources': sources.sel(**{group_by.dimension: [tile_index]}),
                    'geobox': observation['geobox']
                }
        return stack

    def list_cells(self, cell_index=None, **query):
        """
        List cell that match the query.

        Cells are included if they contain any datasets that match the query using the same format as
        :meth:`datacube.Datacube.load`.

        E.g.::

            gw.list_cells(product_type='nbar',
                          platform=['LANDSAT_5', 'LANDSAT_7', 'LANDSAT_8'],
                          time=('2001-1-1 00:00:00', '2001-3-31 23:59:59'))

        :param (int,int) cell_index: The cell index. E.g. (14, -40)
        :param query: see :py:class:`datacube.api.query.Query`
        :rtype: dict[(int, int), Cell]
        """
        observations = self.cell_observations(cell_index, **query)
        return self.cell_sources(observations, query_group_by(**query))

    def list_tiles(self, cell_index=None, **query):
        """
        List tiles of data, sorted by cell.
        ::

            tiles = gw.list_tiles(product_type=['nbar', 'pq'], platform='LANDSAT_5')

        The values can be passed to :meth:`load`

        :param (int,int) cell_index: The cell index. E.g. (14, -40)
        :param query: see :py:class:`datacube.api.query.Query`
        :rtype: dict[(int, int, numpy.datetime64), Tile]

        .. seealso:: :meth:`load`
        """
        observations = self.cell_observations(cell_index, **query)
        return self.tile_sources(observations, query_group_by(**query))

    @staticmethod
    def load(tile, measurements=None, dask_chunks=None):
        """
        Load data for a cell/tile.

        The data to be loaded is defined by the output of :meth:`list_tiles`.

        See the documentation on using `xarray with dask <http://xarray.pydata.org/en/stable/dask.html>`_
        for more information.

        :param tile: The tile to load.

        :param measurements: The name or list of names of measurements to load

        :param dict dask_chunks: If the data should be loaded as needed using :py:class:`dask.array.Array`,
            specify the chunk size in each output direction.

            See the documentation on using `xarray with dask <http://xarray.pydata.org/en/stable/dask.html>`_
            for more information.

        :return: The requested data.
        :rtype: :py:class:`xarray.Dataset`

        .. seealso::
            :meth:`list_tiles` :meth:`list_cells`
        """
        sources = tile['sources']
        geobox = tile['geobox']

        observations = []
        for dataset in sources.values:
            observations += dataset

        all_measurements = get_measurements(observations)
        if measurements:
            measurements = [all_measurements[measurement] for measurement in measurements
                            if measurement in all_measurements]
        else:
            measurements = [measurement for measurement in all_measurements.values()]

        dataset = Datacube.product_data(sources, geobox, measurements, dask_chunks=dask_chunks)

        return dataset

    def __str__(self):
        return "GridWorkflow<index={!r},\n\tgridspec={!r}>".format(self.grid_spec, self.index)

    def __repr__(self):
        return self.__str__()
