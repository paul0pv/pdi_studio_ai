# video_capture/camera_utils.py

import cv2
# import logging


def list_available_cameras(
    max_index: int = 10, require_frame: bool = True, verbose: bool = False
) -> list:
    """
    Escanea los índices de cámara disponibles usando OpenCV.

    Args:
        max_index (int): Índice máximo a probar (por defecto 10).
        require_frame (bool): Si True, requiere que la cámara devuelva un frame válido.
        verbose (bool): Si True, imprime información de depuración.

    Returns:
        list: Lista de índices de cámara disponibles.
    """
    available = []

    for index in range(max_index):
        try:
            cap = cv2.VideoCapture(
                index, cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") else 0
            )
            if not cap.isOpened():
                if verbose:
                    print(f"[CameraUtils] Cámara {index} no se pudo abrir.")
                continue

            if require_frame:
                ret, _ = cap.read()
                if not ret:
                    if verbose:
                        print(
                            f"[CameraUtils] Cámara {index} abierta pero no devuelve frame."
                        )
                    cap.release()
                    continue

            available.append(index)
            if verbose:
                print(f"[CameraUtils] Cámara {index} disponible.")
            cap.release()

        except Exception as e:
            print(f"[CameraUtils] ❌ Error probando cámara {index}: {str(e)}")

    return available
