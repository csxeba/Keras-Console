import time
import socket
import threading

from keras.models import Model
from keras.callbacks import Callback


class KerasConsoleServer(Callback):

    message_separator = "<(O.o)>"

    def __init__(self, port_num=7199):
        super().__init__()
        self.port_num = port_num
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", port_num))
        self.connection = None  # type: socket.socket
        self._listening_worker = threading.Thread(target=self._listening_job,
                                                  name="ListeningWorker")
        self._messaging_worker = threading.Thread(target=self._messaging_job,
                                                  name="MessagingWorker")
        self.callback_mapping = {"end-training": self._end_training_callback,
                                 "save-model": self._save_model_callback}
        self.commands = []
        self.model = self.model  # type: Model

    def _end_training_callback(self):
        self.model.stop_training = True

    def _save_model_callback(self, path=None):
        path = path or (self.model.name + ".h5")
        self.model.save(path)

    def on_batch_end(self, batch, logs=None):
        if len(self.commands) == 0:
            return
        for command in self.commands:
            callback = self.callback_mapping.get(command)
            if callback is None:
                print("Unknown command:", command)
                continue
            print("Executing command:", command)
            callback()

    def _listening_job(self):
        self.socket.listen(0)
        conn, addr = self.socket.accept()
        self.connection = conn
        self.connection.settimeout(1.)

    def _messaging_job(self):
        messages = ""
        while 1:
            if self.connection is None:
                time.sleep(1)
                continue
            try:
                msg = self.connection.recv(1024)
            except socket.error:
                pass
            else:
                messages += msg
            if self.message_separator in messages:
                commands = messages.split(self.message_separator)
                self.commands.extend(commands[:-1])
                messages = commands[-1]
