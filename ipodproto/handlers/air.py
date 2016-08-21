from ..protocol import *
from time import sleep
from typing import Tuple, List, Union
from six.moves.queue import Queue

# Try to use time.monotonic() if it exists, but otherwise time.time() will have to do
try:
    from time import monotonic
except ImportError:
    from time import time as monotonic

try:
    raise TimeoutError()
except TimeoutError:
    pass
except NameError:
    class TimeoutError(Exception):
        pass


class IpodException(Exception):
    pass


class CommandNotUnderstood(IpodException):
    pass


class CommandFailed(IpodException):
    pass


class CommandLengthExceeded(CommandFailed):
    pass


class CommandIsResponse(CommandFailed):
    pass


class AdvancedRemote(IpodProtocolHandler):
    def __init__(self, *args, timeout=1, **kwargs):
        super(AdvancedRemote, self).__init__(*args, **kwargs)

        self._queue = Queue()
        self._timeout = timeout

    def ping(self) -> bool:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.NCU_02

        return self.send_air_command(cmd, True) or True

    def get_flag_ncu_09(self) -> int:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.NCU_09

        return self.send_air_command(cmd, True)

    def set_flag_ncu_0b(self, flag) -> None:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.NCU_0B
        cmd.parameters = int(bool(flag))

        return self.send_air_command(cmd, True).result

    def get_ipod_type(self) -> int:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_IPOD_TYPE

        return self.send_air_command(cmd, True)

    def get_ipod_name(self) -> str:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_IPOD_NAME

        return self.send_air_command(cmd, True).text

    def switch_main_playlist(self) -> None:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.SWITCH_MAIN_PLAYLIST

        self.send_air_command(cmd)

    def switch_item(self, type: int, number: int) -> None:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.SWITCH_ITEM
        cmd.parameters = ItemParam()
        cmd.parameters.type = type
        cmd.parameters.number = number

        self.send_air_command(cmd)
        # FIXME do we also want to send the execute command?

    def get_item_count(self, type: int) -> int:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_TYPE_COUNT
        cmd.parameters = type

        return self.send_air_command(cmd, True)

    def get_item_names(self, type: int, start, count) -> List[str]:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_ITEM_NAMES
        cmd.parameters = ItemRangeParam()
        cmd.parameters.type = type
        cmd.parameters.start = start
        cmd.parameters.length = count

        # Don't wait for the command, we require a different method
        self.send_air_command(cmd, False)

        return self.get_names_response(count, timeout=self._timeout * 4)

    def get_time_status_info(self) -> Tuple[int, int, int]:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_TIME_STATUS

        res = self.send_air_command(cmd, True)

        return res.length, res.elapsed, res.status

    def get_playlist_position(self) -> int:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_PLAYLIST_POS

        return self.send_air_command(cmd, True)

    def get_song_title(self, index: int) -> str:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_SONG_TITLE
        cmd.parameters = index

        return self.send_air_command(cmd, True).text

    def get_song_artist(self, index: int) -> str:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_SONG_ARTIST
        cmd.parameters = index

        return self.send_air_command(cmd, True).text

    def get_song_album(self, index: int) -> str:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_SONG_ALBUM
        cmd.parameters = index

        return self.send_air_command(cmd, True).text

    def set_polling_mode(self, mode) -> None:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.SET_POLLING_MODE
        cmd.parameters = int(bool(mode))

        self.send_air_command(cmd, False)

    def on_poll_update(self, elapsed: int) -> None:
        pass

    def playback_control(self, control: int) -> None:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.PLAYBACK_CONTROL
        cmd.parameters = control

        self.send_air_command(cmd, False)

    def play_pause(self) -> None:
        self.playback_control(CONTROL_PLAY_PAUSE)

    def stop_playing(self) -> None:
        self.playback_control(CONTROL_STOP)

    def skip_forward(self) -> None:
        self.playback_control(CONTROL_SKIP_FORWARD)

    def skip_backward(self) -> None:
        self.playback_control(CONTROL_SKIP_BACKWARD)

    def start_fastforward(self) -> None:
        self.playback_control(CONTROL_FAST_FORWARD)

    def start_rewind(self) -> None:
        self.playback_control(CONTROL_REWIND)

    def stop_ff_rw(self) -> None:
        self.playback_control(CONTROL_STOP_FFRW)

    def get_shuffle_mode(self) -> int:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_SHUFFLE_MODE

        return self.send_air_command(cmd, True)

    def set_shuffle_mode(self):
        cmd = AirCommand()
        cmd.id = AirMode.Commands.SET_SHUFFLE_MODE

        self.send_air_command(cmd, False)

    def get_repeat_mode(self) -> int:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_REPEAT_MODE

        return self.send_air_command(cmd, True)

    def set_repeat_mode(self) -> None:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.SET_REPEAT_MODE

        self.send_air_command(cmd, False)

    def upload_picture(self, picture) -> None:
        raise NotImplementedError()

    def get_playlist_size(self) -> int:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.GET_PLAYLIST_SIZE

        return self.send_air_command(cmd, True)

    def jump_to_song(self, index) -> None:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.PLAYLIST_JUMP
        cmd.parameters = index

        self.send_air_command(cmd, False)

    def get_ncu_39(self) -> None:
        cmd = AirCommand()
        cmd.id = AirMode.Commands.NCU_38

        self.send_air_command(cmd, False)

    def packet_received(self, packet: IpodPacket) -> None:
        if packet.command.id == AirMode.Commands.RES_TIME_ELAPSED:
            # Polling isn't quite a response, so don't clog up the queue with it
            self.on_poll_update(packet.command.parameters.elapsed)
        else:
            self._queue.put_nowait((packet.command, monotonic() + self._timeout))

    def send_air_command(self, cmd: AirCommand, wait: bool = False) -> Union[int, StringField, ItemNameResult,
                                                                                 TimeStatusResult, ScreenSizeResult,
                                                                                 CommandResultParam]:
        packet = IpodPacket()
        packet.mode = MODE_ADVANCED_REMOTE
        packet.command = cmd

        self.send_packet(packet)

        if wait:
            return self.wait_for_response(command.id)

    def get_names_response(self, count, timeout=None) -> List[str]:
        """
        Handles the multiple responses for the get_item_names method.
        :return:
        """
        end = monotonic() + timeout or self._timeout

        results = []

        while monotonic() <= end:
            (res, expiry) = self._queue.get(timeout=(timeout or self._timeout) / 2)
            if res.id == AirMode.Commands.GET_ITEM_NAMES:
                results.append((res.parameters, res.parameters.name.text))

                if len(results) == count:
                    break
            else:
                if monotonic() <= expiry:
                    self._queue.put_nowait((res, expiry))
        else:
            # If we didn't break, there was a timeout; make sure we got all items
            if len(results) != count:
                raise TimeoutError("Only {} of {} results were received".format(len(results), count))

        return [name for off, name in sorted(results)]

    def wait_for_response(self, command_id: int):
        """
        Wait for a response to the given command ID to be received. If the command has a corresponding response, its
        parameters will be returned. If an error response is returned, an appropriate exception will be raised. If a
        success response is returned, None is returned.
        :param command_id: The ID of the command for which to retrieve a response. NOT the response ID!
        :return: The parameters of the response, or None for a success response.
        """
        end = monotonic() + self._timeout
        while monotonic() <= end:
            (res, expiry) = self._queue.get(timeout=self._timeout / 2)
            if res.id == command_id + 1:
                # Response IDs are always command ID + 1
                return res.parameters
            elif res.id == AirMode.Commands.NCU_00 and res.parameters.command == command_id:
                raise CommandNotUnderstood()
            elif res.id == AirMode.Commands.FEEDBACK and res.parameters.command == command_id:
                if res.parameters.result == RESULT_SUCCESS:
                    return None
                elif res.parameters.result == RESULT_FAILURE:
                    raise CommandFailed()
                elif res.parameters.result == RESULT_BAD_LENGTH:
                    raise CommandLengthExceeded()
                elif res.parameters.result == RESULT_RESPONSE_NOT_COMMAND:
                    raise CommandIsResponse()
            else:
                empty = self._queue.empty()

                if monotonic() <= expiry:
                    # Only put it back through the queue if it hasn't expired
                    self._queue.put_nowait((res, expiry))

                if empty:
                    # If we just emptied the queue, wait a bit instead of pegging it
                    sleep(min(.05, self._timeout))

        raise TimeoutError()
