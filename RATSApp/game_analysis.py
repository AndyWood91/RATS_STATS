# !/usr/bin/env python
# -*- coding: utf-8 -*-

# open a game file
# read through points
# read through sequences
# read through possessions
# read through discs

# spit out numbers for both teams and each player in each team.
# TAG'd
# MON'd

# retention == passes completed per pass attempted  # TODO: individual player stats, different for shot takers
# efficiency == goals scored per possession  # TODO: where is the win line? above what percentage?
# conversions == goals scored per point played  # TODO: what lines are most efficient at conversions

# imports

# standard library
import sys, os
import pickle

# local project
import raw_game_hierarchy as rgh
import storage_operations as stops
import internet_operations as int_ops

# TODO: work out how to extend classes in RGH


class Root(object):
    """
    Wrapper class for debugging.
    """

    def __init__(self, **kwargs):
        """
        Raises an assertion error if any unexpected kwargs exist on initialisation.
        """

        if kwargs:
            print(kwargs)  # Andy - if these exist we need to work out why
            print("Root.__init__() called.")

        assert not kwargs


class AnalysedTeam(Root):
    """storage unit for Team level statistics for a Game object."""

    def __init__(self, **kwargs):
        """
        Parameters:
             team_name, team_coaches, team_players, team_opponent, 
             as mandatory arguments.
        """

        # Game Descriptors
        self.team_name = kwargs.pop("team_name")  # string
        self.team_coaches = kwargs.pop("team_coaches")  # list of Coach objects
        self.team_players = kwargs.pop("team_players")  # list of Player objects
        self.team_opponent = kwargs.pop("team_opponent")  # string - matches team.name

        """
        Conversions: Goals Scored Per Point Played
        """

        # Points
        self.team_points = 0  # count

        self.team_offences = 0  # count of points on offence
        self.team_offences_without_turnover = 0
        self.team_offences_held = 0
        self.team_offences_with_turnover = 0
        self.team_offences_broken = 0
        self.team_offensive_conversion_rate = 0.00  # goals scored per offensive point played

        self.team_defences = 0  # count of points on defence
        self.team_defences_without_turnover = 0
        self.team_defences_held = 0
        self.team_defences_with_turnover = 0
        self.team_defences_broken = 0
        self.team_defensive_conversion_rate = 0.00  # goals scored per offensive point played

        # TODO: could do a sum check on the conversion rates, if it's over 100% you win the game

        """
        Efficiency: Goals Scored Per Possession
        """

        self.team_possessions = 0
        self.team_possessions_goal = 0
        self.team_possessions_turnover = 0
        self.team_efficiency = 0.00

        # Offence
        self.team_offensive_possessions = 0  # count
        self.team_offensive_possessions_goal = 0
        self.team_offensive_possessions_turnover = 0
        self.team_offensive_efficiency = 0.00  # goals scored per offensive possession

        # Defence
        self.team_defensive_possessions = 0  # count
        self.team_defensive_possessions_goal = 0
        self.team_defensive_possessions_turnover = 0
        self.team_defensive_efficiency = 0.00  # goals scored per defensive possession

        """
        Retention: Passes Completed Per Pass Attempted
        """

        # Touches
        self.team_discs = 0  # any time someone established possession of the disc
        self.team_completions = 0  # any successful transfer of possession to another player on the same team
        self.team_turnovers = 0  # unsuccessful transfer attempt
        self.team_retention_rate = 0.00  #

        # Offence
        self.team_offensive_discs = 0
        self.team_offensive_completions = 0
        self.team_offensive_turnovers = 0
        self.team_offensive_retention_rate = 0.00  # percentage

        # Defence
        self.team_defensive_discs = 0
        self.team_defensive_completions = 0
        self.team_defensive_turnovers = 0
        self.team_defensive_retention_rate = 0.00

        # Goals
        self.team_goals = []  # list of player pairs, can count len() for the score

        # Defences
        self.team_defences = []  # list of players who created turnovers, should include the point index

        """
        DEAD RATS: statistics to pull out after a game
        """

        # self.team_offensive_structures = []  # TODO: list of initial play calls, done after the Game
        # self.team_defensive_structures = []  # TODO: list of defensive calls, done after the Game
        # TODO: offensive_points + defensive_points == points_played

        # TODO: on/off numbers, player valuations

        super(AnalysedTeam, self).__init__(**kwargs)


class AnalysedPlayer(Root):
    """
    storage unit for Player level statistics for a Game object.
    """

    def __init__(self, **kwargs):
        """
        Parameters:
             takes player_name, player_number, player_gender
             as mandatory inputs.
        """

        # Descriptors
        self.player_name = kwargs.pop("player_name")
        self.player_number = kwargs.pop("player_number")
        self.player_gender = kwargs.pop("player_gender")

        """
        Player Valuations: On/Off Numbers
        """

        # Points
        self.player_points = 0

        # Offence
        self.player_offences = 0  # offensive points
        self.player_offences_without_turnover = 0
        self.player_offences_held = 0
        self.player_offences_with_turnover = 0
        self.player_offences_broken = 0

        # Defence
        self.player_defences = 0  # defensive points
        self.player_defences_without_turnover = 0
        self.player_defences_held = 0
        self.player_defences_with_turnover = 0
        self.player_defences_breaks = 0

        """
        Possession Statistics On Offence: Probably a Team level analysis? Connections should go here.
        """

        self.player_offensive_possessions = 0  # TeamPossessions which include the player, want a percentage eventually
        self.player_offensive_possessions_goal = 0
        self.player_offensive_possessions_turnover = 0

        # defensive possessions only occur after a turnover, so not giving it back is very important
        self.player_defensive_possessions = 0  # TeamPossessions which include the player, want a percentage eventually
        self.player_defensive_possessions_goal = 0
        self.player_defensive_possessions_turnover = 0

        """
        Player Statistics: Who's Playing Well
        """

        # PlayerDiscs
        # Offence
        self.player_touches = 0
        self.player_completions = 0
        self.player_turnovers = 0
        self.player_assists = 0
        self.player_goals = 0
        self.player_completion_rate = 0.00

        # Defence
        self.player_defences = 0
        # TODO: completion_rate = completions / touches

        # Mixed
        self.throws_to_same_gender = 0
        self.throws_to_opposite_gender = 0

        self.turnovers_to_same_gender = 0
        self.turnovers_to_opposite_gender = 0

        self.goals_to_same_gender = 0
        self.goals_to_opposite_gender = 0

        self.more_women_points_played = 0
        self.more_men_points_played = 0

        super(AnalysedPlayer, self).__init__(**kwargs)


def edit_game(game):
    # test match 2
    # aus v jpn
    fixed_game = game
    first_p = fixed_game.points[0]
    first_p.sequences.pop(0)
    first_p.sequences[0].events.pop() # remove brendo goal
    japan_fake = rgh.Player(player_name='Japan',
                          player_number=-1,
                          player_gender='T')
    japan_22 = rgh.Player(player_name='Taku HONNA',
                          player_number=22,
                          player_gender='m')
    japan_31 = rgh.Player(player_name='Yuko SATO',
                          player_number=31,
                          player_gender='f')
    japan_15 = rgh.Player(player_name='Saori INOUE',
                          player_number=15,
                          player_gender='f')

    first_p.sequences[0].events.append(rgh.Event(event_player=japan_fake,
                                                event_action='hand-block',
                                                 ts_start=0))
    first_p.sequences[0].events.append(rgh.Event(event_player=japan_22,
                                                event_action='pass',
                                                 ts_start=0))
    first_p.sequences[0].events.append(rgh.Event(event_player=japan_31,
                                                event_action='pass',
                                                 ts_start=0))
    first_p.sequences[0].events.append(rgh.Event(event_player=japan_15,
                                                event_action='pass',
                                                 ts_start=0))
    first_p.sequences[0].events.append(rgh.Event(event_player=japan_22,
                                                event_action='goal',
                                                 ts_start=0))

    return fixed_game


def run_gender_analysis(player,game):

    player_statistics = AnalysedPlayer(
        player_name=player.player_name,
        player_number=player.player_number,
        player_gender=player.player_gender,
    )

    for point in game.points:
        playing_this_point_flag = False
        for sequence in point.sequences:
            # if they're not in this sequence, skip
            if player.player_name not in [a.player_name for a in sequence.lines[0]] \
                    and player.player_name not in [b.player_name for b in sequence.lines[1]] \
                    and player.player_gender != 'T':

                continue
            playing_this_point_flag = True

            for i in range(0, len(sequence.events)):

                event = sequence.events[i]
                #print('event - player : '+str(event.event_action)+' - '+str(event.event_player.player_name))
                # if this event relates to this player
                if event.event_player.player_name == player.player_name:
                    player_statistics.player_touches += 1
                    if i < len(sequence.events)-1:  # dont go past the end - better safe than sorry
                        # don't know who the throw was for if it got blocked
                        if sequence.events[i+1].event_action != 'block':

                            if sequence.events[i+1].event_player.player_gender == player_statistics.player_gender:
                                player_statistics.throws_to_same_gender += 1
                                if sequence.events[i + 1].event_action in rgh.Event.turnover_actions:
                                    player_statistics.turnovers_to_same_gender += 1
                                elif sequence.events[i+1].event_action == 'goal':
                                    player_statistics.goals_to_same_gender += 1

                            elif sequence.events[i+1].event_player.player_gender != player_statistics.player_gender:
                                player_statistics.throws_to_opposite_gender += 1
                                if sequence.events[i + 1].event_action in rgh.Event.turnover_actions:
                                    player_statistics.turnovers_to_opposite_gender += 1
                                elif sequence.events[i+1].event_action == 'goal':
                                    player_statistics.goals_to_opposite_gender += 1

        if playing_this_point_flag:
            player_statistics.player_points+=1

    return player_statistics


def run_player_analysis(player, game):

    player_statistics = AnalysedPlayer(
        player_name=player.player_name,
        player_number=player.player_number,
        player_gender=player.player_gender,
    )

    for point in game.points:  # loop over points
        playing_this_point_flag = False
        #if game.points.index(point) != 0:
        #    break # only looking at the first point
        for sequence in point.sequences:  # loop over sequences

            # if the player is not in this sequence
            if player.player_name not in [a.player_name for a in sequence.lines[0]] \
                    and player.player_name not in [b.player_name for b in sequence.lines[1]] \
                    and player.player_gender != 'T':
                    # consider working out how to do __eq__ and __ne__ properly

                continue
            playing_this_point_flag = True

            for i in range(0, len(sequence.events)):

                event = sequence.events[i]
                #print('event - player : '+str(event.event_action)+' - '+str(event.event_player.player_name))

                if event.event_player.player_name == player.player_name:

                    # single-check events
                    player_statistics.player_touches += 1

                    # Checks on the current event

                    if event.event_action == 'goal':
                        print('goal scored by: '+str(player_statistics.player_name))
                        player_statistics.player_goals += 1

                    if event.event_action == 'block' or event.event_action == 'intercept':
                        player_statistics.player_defences += 1
                        print('block by: '+str(player_statistics.player_name))

                    # Checks on the following event

                    if i < len(sequence.events)-1:  # dont go past the end - better safe than sorry
                        #print(str(i)+'#'+str('ll'))
                        if sequence.events[i+1].event_action == 'goal':
                            #print('assist thrown by: ' + str(player_statistics.player_name))
                            player_statistics.player_assists += 1
                        if sequence.events[i+1].event_action in rgh.Event.turnover_actions:
                            player_statistics.player_turnovers += 1
                            print('turnover for: ' + str(player_statistics.player_name))


                    # test 2
                    # aus 26
                    # jpn 12

            # calculated stats - these numbers to be run after reading over the whole game (for a player)
            if player_statistics.player_touches != 0:
                # print('{} / {} ').format(player_statistics.player_turnovers, player_statistics.player_touches)
                player_statistics.completion_rate =\
                    player_statistics.player_turnovers / player_statistics.player_touches

            else:
                player_statistics.completion_rate = 1.00

        if playing_this_point_flag:
            player_statistics.player_points+=1

    return player_statistics


def point_progressions(game):
    """Points in the Game."""

    return [point for point in game.points]


def sequence_progressions(game):
    """Sequences in a Point"""

    return [[sequence for sequence in point.sequences] for point in game.points]


def possession_progression(analysed_game):
    """TeamPossessions in a Sequence."""

    starting_offence_possessions = [[]]
    starting_defence_possessions = [[]]

    for point in analysed_game.points:
        # print(point)
        print("\n")

        for sequence in point.sequences:
            print("starting offence: {}".format(sequence.offence))

            print("sequence length: {}".format(len(sequence.events)))
            for event in sequence.events:
                print(event)

                # TODO: Andy - this needs to check Australia or Japan
                if event.event_action != u"goal":

                    if event.event_action not in rgh.Event.turnover_actions:

                        if event.event_player in analysed_game.teams[0].team_players:  # starting offence
                            starting_offence_possessions[0].append(event)
                        elif event.event_player in analysed_game.teams[1].team_players:
                            starting_defence_possessions[0].append(event)
                        else:
                            raise ValueError  # something has gone wrong with the team check


def discs_progression():
    """PlayerDiscs in a TeamPossession"""

    pass


def calculate_maidens(analysed_game):

    team_maidens = []

    for a in range(0, len(analysed_game.teams)):

        for point in analysed_game.points:

            for sequence in analysed_game.sequences:

                sequence_maidens = []

                if sequence.offence == analysed_game.teams[a]:  # if the team is starting this sequence on offence
                    continue  # not interested in maidens

                # ANDY - I don't think I want the nested in an elif, but maybe I do?
                print(sequence.lines[a])


def main():
    """"""

    # game_filename = 'Test Match Series2017_Australia_Japan_final.p'  # test match 1
    game_filename = 'Test Match Series_Game22017_Australia_Japan_fixed1.p' # test match 2

    # spreadsheet_id = '118UBChrwhwPEf3-XqthPNSo3ksPVKaUIfbj8ruv5Z1E' # test match 1
    spreadsheet_id = '1aY4L_kNn_y7HuG7AYD7Vv0D3mVF_XqxxpD-Nt1qjMe0' # test match 2

    # spreadsheet_id = '1f98e2VyU3Y6SVQ1nSeDl3QnrTAl7S5e2Y8MptNi-j5A' # test match 1 - gender
    # spreadsheet_id = '1dAuFwK7oWXBsaZQZ6ogpZ56XWa3bDQ_20kWDK97J_pw' # test match 2 - gender

    # spreadsheet_id = '1pV7Z2uWvxtRI-N2WX75I77wvJPXiaE2FQpuZWio4zFc'  # WUGC2016 Random Game AUSvCAN

    # first edit was to fix incorrectly assigned first goal

    # copy pickle from stat taking to stat output working dir
    #stops.pipe_pickle_to_output(game_filename,
    #                            'C:\Users\\robsw\AppData\Roaming\stats',
    #                            'C:\Users\\robsw\PycharmProjects\RATS_STATS\RATSApp')

    storage_name = os.path.join('Storage',game_filename)

    analysed_game = stops.retrieve_game_pickle(storage_name)

    # edit the game using edit_game
    #   analysed_game = edit_game(analysed_game)
    # then store
    #   stops.store_game_pickle(analysed_game,'C:\Users\\robsw\PycharmProjects\RATS_STATS\RATSApp\Test Match Series_Game22017_Australia_Japan_fixed1.p')

    print('num points = '+str(len(analysed_game.points)))

    for team in analysed_game.teams:
        data = []
        for player in team.team_players:
            this_player = run_player_analysis(player, analysed_game)
            # this_player = run_gender_analysis(player, analysed_game)

            # TODO: work out a better way of coding new analysis and swapping between them

            # standard analysis
            data.append([str(this_player.player_name),this_player.player_number, this_player.player_gender,
                         this_player.player_points, this_player.player_touches,
                         this_player.player_goals, this_player.player_assists, this_player.player_defences,
                         this_player.player_turnovers])

            # gender analysis
            # data.append([str(this_player.player_name), this_player.player_number, this_player.player_gender,
            #            this_player.player_points, this_player.player_touches,
            #             this_player.throws_to_same_gender, this_player.throws_to_opposite_gender,
            #             this_player.turnovers_to_same_gender, this_player.turnovers_to_opposite_gender,
            #             this_player.goals_to_same_gender, this_player.goals_to_opposite_gender])

        # 20/1/17 - this is here only for compatability with the Test Match data - fake player is now built-in
        fakePlayer = rgh.Player(player_gender='T',
                           player_number=-1,
                           player_name=team.team_name)
        this_player = run_player_analysis(fakePlayer,analysed_game)
        # this_player = run_gender_analysis(fakePlayer,analysed_game)

        # standard analysis
        data.append([str(this_player.player_name),this_player.player_number, this_player.player_gender,
                    this_player.player_points, this_player.player_touches,
                    this_player.player_goals, this_player.player_assists, this_player.player_defences,
                    this_player.player_turnovers])

        # gender analysis
        # data.append([str(this_player.player_name), this_player.player_number, this_player.player_gender,
        #             this_player.player_points, this_player.player_touches,
        #             this_player.throws_to_same_gender, this_player.throws_to_opposite_gender,
        #             this_player.turnovers_to_same_gender, this_player.turnovers_to_opposite_gender,
        #             this_player.goals_to_same_gender, this_player.goals_to_opposite_gender])


        int_ops.update_players_sheet(team.team_name, data, spreadsheet_id)


if __name__ == '__main__':
    sys.exit(main())
