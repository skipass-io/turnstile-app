import functools
from pyzbar.pyzbar import decode


class DetectorPyzbar:
    def __init__(self):
        self.decoder = decode

    def detect_qrcode(self, cv_gray):
        """
        QR code detection on the frame
        (if there is more than one QR code, 
        the largest one / closest to the frame will be returned)
        """
        qr_codes = [qr for qr in self.decoder(cv_gray) if qr.type == "QRCODE"]
        if len(qr_codes) == 0:
            return
        qr_code = self._get_qrcode(qr_codes)
        return qr_code.data.decode("utf-8")

    def _get_qrcode(self, qr_codes):
        """
        Returns a QR Code from the array of detected `qr_codes`. 
        (if more than one QR Code is detected, 
        the one with the larger area will be returned.)
        """
        if len(qr_codes) == 1:
            qr_code = qr_codes[0]
        else:
            qr_code = functools.reduce(
                lambda qr_a, qr_b: (
                    qr_a
                    if (qr_a.rect[2] * qr_a.rect[3]) > (qr_b.rect[2] * qr_b.rect[3])
                    else qr_b
                ),
                qr_codes,
            )
        return qr_code
