# tools/vision/yolo_detector.py

from __future__ import annotations

import os
from typing import Any, List, Dict

from ultralytics import YOLO
from PIL import Image

from ..base import BaseTool


class YOLODetector(BaseTool):
    """YOLO 目标检测工具。
    
    支持图像目标检测、分类、分割等任务。
    """

    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        confidence: float = 0.5,
        output_dir: str = "./output/yolo",
    ):
        super().__init__(
            name="yolo_detector",
            description="使用 YOLO 进行目标检测，识别图像中的物体",
            parameters={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "要检测的图像文件路径",
                    },
                    "task": {
                        "type": "string",
                        "description": "任务类型: detect(检测), segment(分割), classify(分类)",
                        "enum": ["detect", "segment", "classify"],
                        "default": "detect",
                    },
                    "save_result": {
                        "type": "boolean",
                        "description": "是否保存标注后的图像",
                        "default": True,
                    },
                },
                "required": ["image_path"],
            },
        )
        self.model_name = model_name
        self.confidence = confidence
        self.output_dir = output_dir
        self._model = None  # 延迟加载

    @property
    def model(self) -> YOLO:
        """延迟加载模型。"""
        if self._model is None:
            self._model = YOLO(self.model_name)
        return self._model

    def execute(
        self,
        image_path: str,
        task: str = "detect",
        save_result: bool = True,
    ) -> str:
        """执行目标检测。"""
        if not os.path.exists(image_path):
            return f"❌ 错误：图像文件不存在 - {image_path}"

        try:
            # 运行推理
            results = self.model(
                image_path,
                conf=self.confidence,
                save=save_result,
                project=self.output_dir,
            )

            # 解析结果
            detections = []
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = result.names[cls_id]
                    conf = float(box.conf[0])
                    detections.append(f"{cls_name}: {conf:.2%}")

            if detections:
                output = f"✅ 检测到 {len(detections)} 个目标:\n"
                output += "\n".join(f"  • {d}" for d in detections)
            else:
                output = "未检测到目标"

            if save_result:
                output += f"\n📁 结果已保存至: {self.output_dir}"

            return output

        except Exception as e:
            return f"❌ 检测失败: {e}"