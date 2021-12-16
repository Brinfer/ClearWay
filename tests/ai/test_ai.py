"""Bicycles detection test with YOLO and openCV."""
from clearway.ai import ai
from pytest_mock import MockerFixture


def test_initialise_ai_instance(mocker: MockerFixture) -> None:
    """Test of the instance creation method."""
    __on_raspberry = False
    __see_real_time_processing = False
    __yolo_weights = "yolov2-tiny.weights"
    __yolo_cfg = "yolov2-tiny.cfg"
    __size = 416
    __path_to_input_video = None
    __path_to_output_video = None

    spy = mocker.spy(ai.Ai, "__init__")
    # mocker.patch('cv2.dnn.readNet', side_effect=mock_cv2_dnn_readnet)

    mock_cv2_dnn_readnet = mocker.Mock()
    mock_cv2_dnn_readnet.getLayerNames.side_effect = [
        [
            "conv_0",
            "bn_0",
            "leaky_1",
            "pool_1",
            "conv_2",
            "bn_2",
            "leaky_3",
            "pool_3",
            "conv_4",
            "bn_4",
            "leaky_5",
            "pool_5",
            "conv_6",
            "bn_6",
            "leaky_7",
            "pool_7",
            "conv_8",
            "bn_8",
            "leaky_9",
            "pool_9",
            "conv_10",
            "bn_10",
            "leaky_11",
            "pool_11",
            "conv_12",
            "bn_12",
            "leaky_13",
            "conv_13",
            "bn_13",
            "leaky_14",
            "conv_14",
            "permute_15",
            "detection_out",
        ]
    ]
    mock_cv2_dnn_readnet.getUnconnectedOutLayers.side_effect = [[[33]]]
    mock_cv2 = mocker.patch("cv2.dnn.readNet")
    mock_cv2.return_value = mock_cv2_dnn_readnet

    ai_instance = ai.Ai(
        __on_raspberry,
        __see_real_time_processing,
        __yolo_weights,
        __yolo_cfg,
        __size,
        __path_to_input_video,
        __path_to_output_video,
    )
    assert spy.call_count == 1
    assert ai_instance is not None, "Error, the ai_instance is None"


def test_no_input_video_no_output_video():
    """Camera video stream processing test without output video."""


def test_no_input_video_output_video():
    """Camera video stream processing test with output video."""


def test_input_video_no_output_video():
    """Input video processing test without output video."""


def test_input_video_output_video():
    """Input video processing test with output video."""
