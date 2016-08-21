import threading

import time

from ..protocol import *


class IpodEmulator(IpodProtocolHandler):
    """
    Used for client devices that wish to emulate an iPod in order to interface with an accessory.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mode = MODE_SWITCH

        # Who knows what this actually does. Apparently it should be reset when changing tracks, though.
        self.flag_ncu_0b = 0x00

        # Pick some random ipod type to begin with
        self.ipod_type = IPOD_TYPE_GEN5_30GB

        # Default iPod name
        self.ipod_name = "iPod"

        self.status = STATUS_STOP

        self.polling_thread = None
        self.polling = False

        self.target_playlist = 0

        self.shuffle_mode = SHUFFLE_OFF
        self.repeat_mode = REPEAT_OFF

        self.screen_size = (310, 168)

    def packet_received(self, packet: IpodPacket):
        if packet.mode == MODE_SWITCH:
            self.handle_mode_switch_command(packet.command)
        elif packet.mode == MODE_VOICE_RECORDER:
            self.handle_voice_recorder_command(packet.command)
        elif packet.mode == MODE_SIMPLE_REMOTE:
            self.handle_simple_remote_command(packet.command)
        elif packet.mode == MODE_REQUEST_MODE_STATUS:
            self.handle_request_mode_status_command(packet.command)
        elif packet.mode == MODE_ADVANCED_REMOTE:
            self.handle_advanced_remote_command(packet.command)

    def handle_mode_switch_command(self, command: SwitchModeCommand):
        if command.id == SwitchMode.Commands.SET_VOICE_RECORDER:
            self.mode = MODE_VOICE_RECORDER
        elif command == SwitchMode.Commands.SET_IPOD_REMOTE or \
                command == SwitchMode.Commands.SET_IPOD_REMOTE_ALT:
            self.mode = MODE_SIMPLE_REMOTE
        elif command == SwitchMode.Commands.SET_ADVANCED_REMOTE or \
                command == SwitchMode.Commands.SET_ADVANCED_REMOTE_ALT:
            self.mode = MODE_ADVANCED_REMOTE
        elif command == SwitchMode.Commands.GET_MODE:
            self._send_get_mode_response()

    def _send_get_mode_response(self):
        res = IpodPacket()
        res.mode = MODE_SWITCH
        res.command = SwitchModeCommand()

        if self.mode == MODE_SWITCH:
            res.command.id = SwitchMode.Commands.RES_MODE_SWITCH
        elif self.mode == MODE_VOICE_RECORDER:
            res.command.id = SwitchMode.Commands.RES_MODE_VOICE_RECORDER
        elif self.mode == MODE_SIMPLE_REMOTE:
            res.command.id = SwitchMode.Commands.RES_MODE_IPOD_REMOTE
        elif self.mode == MODE_ADVANCED_REMOTE:
            res.command.id = SwitchMode.Commands.RES_MODE_ADVANCED_REMOTE
        else:
            raise ValueError("Invalid current mode: " + self.mode)

        self.send_packet(res)

    def handle_voice_recorder_command(self, command: VoiceRecorderCommand):
        # The iPod only sends these commands
        pass

    def handle_simple_remote_command(self, command: SimpleRemoteCommand):
        command_map = {
            SimpleRemoteMode.Commands.BUTTON_RELEASED: self.on_button_released,
            SimpleRemoteMode.Commands.PLAY: self.play,
            SimpleRemoteMode.Commands.PAUSE: self.pause,
            SimpleRemoteMode.Commands.PLAY_PAUSE: self.play_pause,
            SimpleRemoteMode.Commands.VOLUME_UP: self.volume_up,
            SimpleRemoteMode.Commands.VOLUME_DOWN: self.volume_down,
            SimpleRemoteMode.Commands.NEXT_SONG: self.skip_forward,
            SimpleRemoteMode.Commands.PREV_SONG: self.skip_backward,
            SimpleRemoteMode.Commands.NEXT_ALBUM: self.next_album,
            SimpleRemoteMode.Commands.PREV_ALBUM: self.prev_album,
            SimpleRemoteMode.Commands.STOP: self.stop_playing,
            SimpleRemoteMode.Commands.MUTE: self.mute,
            SimpleRemoteMode.Commands.NEXT_PLAYLIST: self.next_playlist,
            SimpleRemoteMode.Commands.PREV_PLAYLIST: self.prev_playlist,
            SimpleRemoteMode.Commands.SHUFFLE: self.shuffle,
            SimpleRemoteMode.Commands.REPEAT: self.repeat,
            SimpleRemoteMode.Commands.IPOD_OFF: self.off,
            SimpleRemoteMode.Commands.IPOD_ON: self.on,
            SimpleRemoteMode.Commands.MENU_BUTTON: self.menu,
            SimpleRemoteMode.Commands.OK_SELECT_BUTTON: self.select,
            SimpleRemoteMode.Commands.SCROLL_UP: self.scroll_up,
            SimpleRemoteMode.Commands.SCROLL_DOWN: self.scroll_down,
        }

        if command not in command_map:
            raise ValueError("Invalid command for simple remote mode: " + str(command))

        command_map[command]()

    def on_button_released(self):
        pass

    def play(self):
        pass

    def pause(self):
        pass

    def play_pause(self):
        pass

    def volume_up(self):
        pass

    def volume_down(self):
        pass

    def start_fastforward(self):
        pass

    def start_rewind(self):
        pass

    def stop_ff_rw(self):
        pass

    def skip_forward(self):
        pass

    def skip_backward(self):
        pass

    def next_album(self):
        pass

    def prev_album(self):
        pass

    def stop_playing(self):
        pass

    def mute(self):
        pass

    def next_playlist(self):
        pass

    def prev_playlist(self):
        pass

    def shuffle(self):
        pass

    def repeat(self):
        pass

    def off(self):
        pass

    def on(self):
        pass

    def menu(self):
        pass

    def select(self):
        pass

    def scroll_up(self):
        pass

    def scroll_down(self):
        pass

    def handle_request_mode_status_command(self, command: RequestModeStatusCommand):
        self._send_get_mode_response()

    def handle_advanced_remote_command(self, command: AirCommand):
        if command.id == AirMode.Commands.NCU_02:
            # Simple ping command
            self._handle_ping()
        elif command.id == AirMode.Commands.NCU_09:
            # Gets a mystery flag
            self._send_ncu_09_response()
        elif command.id == AirMode.Commands.NCU_0B:
            # Sets the mystery flag
            self._handle_ncu_0b_command(command.parameters)
        elif command.id == AirMode.Commands.NCU_0C:
            self._handle_ncu_0c_command()
        elif command.id == AirMode.Commands.GET_IPOD_TYPE:
            self.handle_get_ipod_type_command()
        elif command.id == AirMode.Commands.GET_IPOD_NAME:
            self.handle_get_ipod_name_command()
        elif command.id == AirMode.Commands.SWITCH_MAIN_PLAYLIST:
            self.switch_main_playlist()
        elif command.id == AirMode.Commands.SWITCH_ITEM:
            self.switch_item(command.parameters.type, command.parameters.number)
        elif command.id == AirMode.Commands.GET_TYPE_COUNT:
            self.handle_get_item_count_command(command.parameters.type)
        elif command.id == AirMode.Commands.GET_ITEM_NAMES:
            self.handle_get_item_names_command(command.parameters.type,
                                               command.parameters.start,
                                               command.parameters.length)
        elif command.id == AirMode.Commands.GET_TIME_STATUS:
            self.handle_get_time_status_command()
        elif command.id == AirMode.Commands.GET_PLAYLIST_POS:
            self.handle_get_playlist_position_command()
        elif command.id == AirMode.Commands.GET_SONG_TITLE:
            self.handle_get_song_title_command(command.parameters)
        elif command.id == AirMode.Commands.GET_SONG_ARTIST:
            self.handle_get_song_artist_command(command.parameters)
        elif command.id == AirMode.Commands.GET_SONG_ALBUM:
            self.handle_get_song_album_command(command.parameters)
        elif command.id == AirMode.Commands.SET_POLLING_MODE:
            self.handle_set_polling_mode(command.parameters)
        elif command.id == AirMode.Commands.EXEC_PLAYLIST_JUMP:
            self.handle_execute_playlist_jump_command(command.parameters)
        elif command.id == AirMode.Commands.PLAYBACK_CONTROL:
            self.handle_playback_control_command(command.parameters)
        elif command.id == AirMode.Commands.GET_SHUFFLE_MODE:
            self.handle_get_shuffle_mode_command()
        elif command.id == AirMode.Commands.SET_SHUFFLE_MODE:
            self.handle_set_shuffle_mode(command.parameters)
        elif command.id == AirMode.Commands.GET_REPEAT_MODE:
            self.handle_get_repeat_mode()
        elif command.id == AirMode.Commands.SET_REPEAT_MODE:
            self.handle_set_repeat_mode(command.parameters)
        elif command.id == AirMode.Commands.UPLOAD_PICTURE:
            # TODO: Implement picture uploading, for whatever reason
            pass
        elif command.id == AirMode.Commands.GET_SCREEN_SIZE:
            self.handle_get_screen_size_command()
        elif command.id == AirMode.Commands.GET_PLAYLIST_SIZE:
            self.handle_get_playlist_size_command()
        elif command.id == AirMode.Commands.PLAYLIST_JUMP:
            self.handle_playlist_jump_command(command.parameters)
        elif command.id == AirMode.Commands.NCU_38:
            # TODO: This is some sort of color get-screen-size command
            pass

    def jump_to_song(self, number):
        pass

    def handle_playlist_jump_command(self, number):
        self.jump_to_song(number)

    def get_playlist_size(self):
        return 0

    def handle_get_playlist_size_command(self):
        res = AirCommand()
        res.id = AirMode.Commands.RES_PLAYLIST_SIZE
        res.parameters = self.get_playlist_size()

    def handle_get_screen_size_command(self):
        res = AirCommand()
        res.id = AirMode.Commands.RES_SCREEN_SIZE
        res.parameters = ScreenSizeResult()
        res.parameters.width, res.parameters.height = self.screen_size
        self.send_air_response(res)

    def handle_set_repeat_mode(self, mode):
        if mode in (REPEAT_OFF, REPEAT_SONG, REPEAT_ALBUM):
            self.repeat_mode = mode

    def handle_get_repeat_mode(self):
        res = AirCommand()
        res.id = AirMode.Commands.RES_REPEAT_MODE
        res.parameters = self.repeat_mode
        self.send_air_response(res)

    def handle_set_shuffle_mode(self, mode):
        if mode in (SHUFFLE_OFF, SHUFFLE_SONGS, SHUFFLE_ALBUMS):
            self.shuffle_mode = mode

    def handle_get_shuffle_mode_command(self):
        res = AirCommand()
        res.id = AirMode.Commands.RES_SHUFFLE_MODE
        res.parameters = self.shuffle_mode
        self.send_air_response(res)

    def handle_playback_control_command(self, action):
        if action == CONTROL_PLAY_PAUSE:
            self.play_pause()
        elif action == CONTROL_STOP:
            self.stop_playing()
        elif action == CONTROL_SKIP_FORWARD:
            self.skip_forward()
        elif action == CONTROL_SKIP_BACKWARD:
            self.skip_backward()
        elif action == CONTROL_FAST_FORWARD:
            self.start_fastforward()
        elif action == CONTROL_REWIND:
            self.start_rewind()
        elif action == CONTROL_STOP_FFRW:
            self.stop_ff_rw()

    def handle_execute_playlist_jump_command(self, position):
        """
        I'm not exactly sure what this does... is it only for playlists? Or for all types of 'playlists'? It definitely
        couldn't apply for songs...
        :param position:
        :return:
        """

    def _poll(self):
        packet = IpodPacket()
        packet.mode = MODE_ADVANCED_REMOTE
        packet.command = AirCommand()
        packet.command.id = AirMode.Commands.RES_TIME_ELAPSED

        while self.polling:
            packet.command.parameters = self.get_elapsed_time()
            self.send_packet(packet)
            time.sleep(0.5)

    def start_polling(self):
        if not self.polling_thread:
            self.polling_thread = threading.Thread(target=self._poll)
        if self.polling_thread:
            self.polling_thread.start()

    def stop_polling(self):
        self.polling = False

    def handle_set_polling_mode(self, poll):
        if poll:
            self.start_polling()
        else:
            self.stop_polling()

    def get_song_album_name(self, number):
        return "Song {} Album Name".format(number)

    def get_song_artist_name(self, number):
        return "Song {} Artist Name".format(number)

    def handle_get_song_album_command(self, number):
        res = AirCommand()
        res.id = AirMode.Commands.RES_SONG_ALBUM
        res.parameters = StringField()
        res.parameters.text = self.get_song_album_name(number)
        self.send_air_response(res)

    def handle_get_song_artist_command(self, number):
        res = AirCommand()
        res.id = AirMode.Commands.RES_SONG_ARTIST
        res.parameters = StringField()
        res.parameters.text = self.get_song_artist_name(number)
        self.send_air_response(res)

    def handle_get_song_title_command(self, number):
        # I don't think this is very different from the range ones
        res = AirCommand()
        res.id = AirMode.Commands.RES_SONG_TITLE
        res.parameters = StringField()
        res.parameters.text = self.get_song_name(number)
        self.send_air_response(res)

    def get_playlist_position(self):
        """
        The current track's position in the playlist
        :return: The index of the current track in the current playlist
        """
        return 0

    def handle_get_playlist_position_command(self):
        res = AirCommand()
        res.id = AirMode.Commands.RES_PLAYLIST_POS
        res.parameters = self.get_playlist_position()

        self.send_air_response(res)

    def get_current_track_length(self):
        """
        Currently playing track length in milliseconds
        :return: The length of the currently playing track in milliseconds
        """
        return 0

    def get_elapsed_time(self):
        """
        Elapsed time in milliseconds
        :return: The elapsed time of the current track in milliseconds
        """
        return 0

    def handle_get_time_status_command(self):
        res = AirCommand()
        res.id = AirMode.Commands.RES_TIME_STATUS
        res.parameters = TimeStatusResult()
        res.parameters.length = self.get_current_track_length()
        res.parameters.time = self.get_elapsed_time()
        res.parameters.status = self.status

    def get_playlist_name(self, id):
        return "Playlist {}".format(id)

    def get_artist_name(self, id):
        return "Artist {}".format(id)

    def get_album_name(self, id):
        return "Album {}".format(id)

    def get_genre_name(self, id):
        return "Genre {}".format(id)

    def get_song_name(self, id):
        return "Song {}".format(id)

    def get_composer_name(self, id):
        return "Composer {}".format(id)

    def get_item_name(self, type, number):
        if type == AirMode.Types.PLAYLIST:
            self.get_playlist_name(number)
        elif type == AirMode.Types.ARTIST:
            self.get_artist_name(number)
        elif type == AirMode.Types.ALBUM:
            self.get_album_name(number)
        elif type == AirMode.Types.GENRE:
            self.get_genre_name(number)
        elif type == AirMode.Types.SONG:
            self.get_song_name(number)
        elif type == AirMode.Types.COMPOSER:
            self.get_composer_name(number)

    def handle_get_item_names_command(self, type, start, length):
        names = (self.get_item_name(type, id) for id in range(start, start + length))

        # Make a whole packet so we can reuse it
        packet = IpodPacket()
        packet.mode = MODE_ADVANCED_REMOTE

        res = AirCommand()
        res.id = AirMode.Commands.RES_ITEM_NAME
        res.parameters = ItemNameResult()
        res.parameters.name = StringField()

        packet.command = res

        for id, name in enumerate(names):
            res.parameters.name.text = name
            res.parameters.offset = start + id
            self.send_packet(packet)

    def get_playlist_count(self):
        return 0

    def get_artist_count(self):
        return 0

    def get_album_count(self):
        return 0

    def get_genre_count(self):
        return 0

    def get_song_count(self):
        return 0

    def get_composer_count(self):
        return 0

    def get_item_count(self, type):
        if type == AirMode.Types.PLAYLIST:
            return self.get_playlist_count()
        elif type == AirMode.Types.ARTIST:
            return self.get_artist_count()
        elif type == AirMode.Types.ALBUM:
            return self.get_album_count()
        elif type == AirMode.Types.GENRE:
            return self.get_genre_count()
        elif type == AirMode.Types.SONG:
            return self.get_song_count()
        elif type == AirMode.Types.COMPOSER:
            return self.get_composer_count()

    def handle_get_item_count_command(self, type):
        res = AirCommand()
        res.id = AirMode.Commands.RES_TYPE_COUNT

        res.parameters = self.get_item_count(type)

    def switch_playlist(self, id):
        # We don't actually switch just yet, for some reason?
        self.target_playlist = id

    def switch_artist(self, id):
        pass

    def switch_album(self, id):
        pass

    def switch_genre(self, id):
        pass

    def switch_song(self, id):
        pass

    def switch_composer(self, id):
        pass

    def switch_item(self, type, number):
        if type == AirMode.Types.PLAYLIST:
            self.switch_playlist(number)
        elif type == AirMode.Types.ARTIST:
            self.switch_artist(number)
        elif type == AirMode.Types.ALBUM:
            self.switch_album(number)
        elif type == AirMode.Types.GENRE:
            self.switch_genre(number)
        elif type == AirMode.Types.SONG:
            self.switch_song(number)
        elif type == AirMode.Types.COMPOSER:
            self.switch_composer(number)

    def switch_main_playlist(self):
        """
        Should be overridden. Called when the accessory requests to switch to the main playlist, which contains all songs.
        """
        pass

    def handle_get_ipod_name_command(self):
        res = AirCommand()
        res.id = AirMode.Commands.GET_IPOD_NAME
        res.parameters = StringField()
        res.parameters.text = self.ipod_name

        self.send_air_response(res)

    def handle_get_ipod_type_command(self):
        res = AirCommand()
        res.id = AirMode.Commands.RES_IPOD_TYPE
        res.parameters = self.ipod_type

        self.send_air_response(res)

    def _handle_ncu_0c_command(self):
        res = AirCommand()
        res.id = AirMode.Commands.NCU_0D
        res.parameters = b'\x00' * 11

        self.send_air_response(res)

    def _handle_ncu_0b_command(self, value):
        res = AirCommand()
        res.id = AirMode.Commands.FEEDBACK
        res.parameters = CommandResultParam()
        res.parameters.command = AirMode.Commands.NCU_0B

        if value == 0x01 or value == 0x00:
            self.flag_ncu_0b = value
            res.parameters.result = RESULT_SUCCESS
        else:
            res.parameters.result = RESULT_FAILURE

        self.send_air_response(res)

    def _send_ncu_09_response(self):
        res = AirCommand
        res.id = AirMode.Commands.NCU_0A
        res.parameters = self.flag_ncu_0b

        self.send_air_response(res)

    def _send_ping_response(self):
        res = AirCommand()
        res.id = AirMode.Commands.NCU_03

        self.send_air_response(res)

    def send_air_response(self, command: AirCommand):
        res = IpodPacket()
        res.mode = MODE_ADVANCED_REMOTE
        res.command = command

        self.send_packet(res)

    def _handle_ping(self):
        self._send_ping_response()
