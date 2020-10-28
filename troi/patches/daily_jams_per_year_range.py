import datetime
import random

from troi import Element, Recording, PipelineError
import troi.listenbrainz.recs
import troi.filters
import troi.musicbrainz.recording_lookup
from troi.patches.daily_jams import DailyJamsElement


class DailyJamsPerYearRange(troi.patch.Patch):

    def __init__(self, debug=False):
        troi.patch.Patch.__init__(self, debug)

    @staticmethod
    def inputs():
        return [{ "type": str, "name": "user_name", "desc": "MusicBrainz user name", "optional": False },
                { "type": str, "name": "type", "desc": "The type of daily jam. Must be 'top' or 'similar'.", "optional": False },
                { "type": int, "name": "start_year", "desc": "The start of the year range. (e.g. 1980)", "optional": False },
                { "type": int, "name": "end_year", "desc": "The end of the year range. (e.g. 1989)", "optional": False },
                { "type": int, "name": "day", "desc": "The day of the week to generate jams for (1-7). Leave blank for today.", "optional": True }]
        
    @staticmethod
    def outputs():
        return [Recording]

    @staticmethod
    def slug():
        return "daily-jams-per-year-range"

    @staticmethod
    def description():
        return "Generate a daily playlist from the ListenBrainz recommended recordings focused on a given year range. Day 1 = Monday, Day 2  = Tuesday ..."

    def create(self, inputs):
        user_name = inputs[0]
        type = inputs[1]

        max_year = datetime.datetime.now().year
        min_year = 1800
        try:
            start_year = int(inputs[2])
            if start_year < 1800 or start_year > max_year:
                raise ValueError
        except ValueError:
            raise PipelineError("Invalid value '%s' for start_year. Must be a positive integer between %d and %d. (e.g. 1980)" % (inputs[2], min_year, max_year))

        try:
            end_year = int(inputs[3])
            if start_year < 1800 or start_year > max_year:
                raise ValueError
        except ValueError:
            raise PipelineError("Invalid value '%s' for end_year. Must be a positive integer between %d and %d. (e.g. 1980)" % (inputs[3], min_year, max_year))

        try:
            day = inputs[4]
            if day == None:
                day = 0
        except IndexError:
            day = 0

        if day > 7:
            raise RuntimeError("day must be an integer between 0-7.")
        if day == 0:
            day = datetime.datetime.today().weekday() + 1

        if type not in ("top", "similar"):
            raise PipelineError("type must be either 'top' or 'similar'")

        recs = troi.listenbrainz.recs.UserRecordingRecommendationsElement(user_name=user_name,
                                                                          artist_type=type,
                                                                          count=-1)
        r_lookup = troi.musicbrainz.recording_lookup.RecordingLookupElement()
        r_lookup.set_sources(recs)

        # Filter out tracks that do not fit into the given year range
        year_filter = troi.filters.YearRangeFilterElement(start_year, end_year)
        year_filter.set_sources(r_lookup)

        # If an artist should never appear in a playlist, add the artist_credit_id here
        artist_filter = troi.filters.ArtistCreditFilterElement([])
        artist_filter.set_sources(year_filter)

        artist_limiter = troi.filters.ArtistCreditLimiterElement()
        artist_limiter.set_sources(artist_filter)

        jams = DailyJamsElement(recs, day=day)
        jams.set_sources(artist_limiter)

        return jams
