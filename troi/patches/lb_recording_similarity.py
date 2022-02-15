import click

import troi
import troi.patch
import troi.filters
import troi.utils
import troi.playlist
import troi.listenbrainz.recs
from troi.listenbrainz.dataset_fetcher import DataSetFetcherElement


@click.group()
def cli():
    pass


class LBRecordingSimilarityPatch(troi.patch.Patch):

    @staticmethod
    @cli.command(no_args_is_help=True)
    @click.argument('recording_mbid')
    @click.argument('window_size', default=1)
    @click.argument('filter_artists', default=1)
    def parse_args(**kwargs):
        """
        Find similar recordings from ListenBrainz.

        \b
        RECORDING_MBID: A musicbrainz recording MBID to find similar recordings to
        WINDOW_SIZE: Which window size to choose. Must be 1, 5 or 10
        FILTER_ARTISTS: Filter out same artists. Must be 0 or 1
        """
        return kwargs

    @staticmethod
    def slug():
        return "lb-recording-similarity"

    @staticmethod
    def description():
        return "Find similar recordings from ListenBrainz"

    def create(self, inputs, patch_args):
        recording_mbid = inputs['recording_mbid']
        window_size = inputs['window_size']
        filter_artists = inputs['filter_artists']

        source = DataSetFetcherElement(server_url="https://bono.metabrainz.org/recording-similarity/json",
                                       json_post_data=[{ 'recording_mbid': recording_mbid,
                                                         'window_size': str(window_size),
                                                         'filter_same_artist': str(filter_artists)}])

        pl_maker = troi.playlist.PlaylistMakerElement("Similar recording test playlist",
                                                      "Similar recordings to %s. Window size %d, filter artists %d." % (recording_mbid, window_size, filter_artists),
                                                      patch_slug=self.slug())
        pl_maker.set_sources(source)

        return pl_maker
