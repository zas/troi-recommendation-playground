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
    def parse_args(**kwargs):
        """
        Find similar recordings from ListenBrainz.

        \b
        RECORDING_MBID: A musicbrainz recording MBID to find similar recordings to
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

        source = DataSetFetcherElement(server_url="https://bono.metabrainz.org/recording-similarity/json",
                                       json_post_data=[{ 'recording_mbid': inputs['recording_mbid'] }])

        pl_maker = troi.playlist.PlaylistMakerElement("Similar recording test playlist",
                                                      "Similar recordings to %s" % recording_mbid,
                                                      patch_slug=self.slug())
        pl_maker.set_sources(source)

        return pl_maker
