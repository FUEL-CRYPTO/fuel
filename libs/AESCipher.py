from Crypto.Cipher import AES
import base64


class AESCipher(object):
    def __init__(self, key):
        self.bs = 16
        self.cipher = AES.new(key, AES.MODE_ECB)

    def encrypt(self, raw):
        """
        encrypt(self, raw)

        :param raw:
        :return:

        Encrypt and encode into base64

        """
        raw = self._pad(raw)
        encrypted = self.cipher.encrypt(raw)
        encoded = base64.b64encode(encrypted)
        return str(encoded, 'utf-8')

    def decrypt(self, raw):
        """
        decrypt(self, raw)

        :param raw:
        :return:

        Decode

        """
        decoded = base64.b64decode(raw)
        decrypted = self.cipher.decrypt(decoded)
        return str(self._unpad(decrypted), 'utf-8')

    def _pad(self, s):
        """
        _pad(self, s)

        :param s:
        :return:

        Pad

        """
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        """
        _unpad(self, s)

        :param s:
        :return:

        Unpad

        """
        return s[:-ord(s[len(s) - 1:])]