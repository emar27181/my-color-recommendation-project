"""
実験結果ZIPファイルの解凍・整理モジュール

ZIPファイルからアンケート結果（JSON）と画像を抽出し、
UI・タスク別にディレクトリ構造を整理して保存する。
"""

import os
import json
import zipfile
from pathlib import Path
from typing import Dict, List, Optional


class ExperimentResultExtractor:
    """実験結果の解凍・整理を行うクラス"""

    def __init__(self, base_dir: Optional[str] = None):
        """
        初期化

        Args:
            base_dir: ベースディレクトリのパス
                     Noneの場合はデフォルトパスを使用
        """
        if base_dir is None:
            # デフォルトパス設定
            current_file = Path(__file__).resolve()
            self.base_dir = current_file.parent.parent / "data" / "input" / "experiment_result"
        else:
            self.base_dir = Path(base_dir)

        self.zip_dir = self.base_dir / "zip"
        self.questionnaire_dir = self.base_dir / "questionnaire"
        self.image_dir = self.base_dir / "image"
        self.other_dir = self.questionnaire_dir / "other"

    def extract_all_experiments(self) -> Dict[str, bool]:
        """
        全ての実験結果ZIPファイルを解凍・整理

        Returns:
            Dict[str, bool]: ファイル名と処理成功可否の辞書
        """
        if not self.zip_dir.exists():
            raise FileNotFoundError(f"ZIPディレクトリが見つかりません: {self.zip_dir}")

        results = {}
        zip_files = list(self.zip_dir.glob("experiment_*.zip"))

        if not zip_files:
            print(f"⚠️ ZIPファイルが見つかりません: {self.zip_dir}")
            return results

        print(f"📦 {len(zip_files)}個のZIPファイルを処理します...\n")

        for zip_path in sorted(zip_files):
            participant_name = zip_path.stem.replace("experiment_", "")
            print(f"処理中: {zip_path.name} (参加者: {participant_name})")

            try:
                self.extract_single_experiment(zip_path, participant_name)
                results[zip_path.name] = True
                print(f"✅ 完了: {participant_name}\n")
            except Exception as e:
                results[zip_path.name] = False
                print(f"❌ エラー: {participant_name} - {e}\n")

        return results

    def extract_single_experiment(self, zip_path: Path, participant_id: str):
        """
        単一の実験結果ZIPファイルを解凍・整理

        Args:
            zip_path: ZIPファイルのパス
            participant_id: 参加者ID（ファイル名のベース）
        """
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # ZIPファイル内のファイルリスト取得
            file_list = zip_ref.namelist()

            # JSONファイルの処理
            json_files = [f for f in file_list if f.endswith('.json')]
            if json_files:
                self._process_json(zip_ref, json_files[0], participant_id)

            # 画像ファイルの処理
            image_files = [f for f in file_list if f.endswith('.png')]
            for image_file in image_files:
                self._process_image(zip_ref, image_file, participant_id)

    def _process_json(self, zip_ref: zipfile.ZipFile, json_filename: str, participant_id: str):
        """
        JSONファイルを処理してUI・タスク別に保存

        Args:
            zip_ref: ZIPファイルオブジェクト
            json_filename: JSON ファイル名
            participant_id: 参加者ID
        """
        # JSONデータ読み込み
        with zip_ref.open(json_filename) as f:
            data = json.load(f)

        # メタデータ（その他の情報）を保存
        self._save_metadata(data, participant_id)

        # conditions配列からUI・タスク別データを抽出
        if "conditions" in data:
            for condition in data["conditions"]:
                ui = condition.get("condition", "").lower()  # UI1 or UI2
                material = condition.get("material", "")     # taskA or taskB

                # materialをtask1/task2に変換
                task = self._convert_material_to_task(material)

                if ui and task:
                    self._save_condition_data(condition, ui, task, participant_id)

        # アンケート結果を保存
        if "survey" in data:
            self._save_survey_data(data["survey"], participant_id)

    def _save_metadata(self, data: Dict, participant_id: str):
        """
        メタデータ（参加者情報・デバイス情報・実験全体情報）を保存

        Args:
            data: 実験データ全体
            participant_id: 参加者ID
        """
        self.other_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "participant_id": data.get("participant_id"),
            "participant_info": data.get("participant_info", {}),
            "device": data.get("device", {}),
            "first_ui": data.get("first_ui"),
            "order_pattern": data.get("order_pattern"),
            "experiment_start_time": data.get("experiment_start_time"),
            "experiment_end_time": data.get("experiment_end_time"),
            "total_duration_sec": data.get("total_duration_sec"),
        }

        output_path = self.other_dir / f"{participant_id}_metadata.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _save_condition_data(self, condition: Dict, ui: str, task: str, participant_id: str):
        """
        UI・タスク別の実験条件データを保存

        Args:
            condition: 実験条件データ
            ui: UI種別（ui1 or ui2）
            task: タスク番号（task1 or task2）
            participant_id: 参加者ID
        """
        output_dir = self.questionnaire_dir / ui / task
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{participant_id}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(condition, f, ensure_ascii=False, indent=2)

    def _save_survey_data(self, survey: Dict, participant_id: str):
        """
        アンケート結果を保存

        Args:
            survey: アンケートデータ
            participant_id: 参加者ID
        """
        output_path = self.other_dir / f"{participant_id}_survey.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(survey, f, ensure_ascii=False, indent=2)

    def _process_image(self, zip_ref: zipfile.ZipFile, image_filename: str, participant_id: str):
        """
        画像ファイルを処理してUI・タスク別に保存

        Args:
            zip_ref: ZIPファイルオブジェクト
            image_filename: 画像ファイル名（例: UI1-TaskA_canvas.png）
            participant_id: 参加者ID
        """
        # ファイル名からUI・タスク情報を抽出
        # 例: UI1-TaskA_canvas.png -> ui1, task1
        basename = os.path.splitext(image_filename)[0]  # UI1-TaskA_canvas
        parts = basename.split('-')  # ['UI1', 'TaskA_canvas']

        if len(parts) >= 2:
            ui = parts[0].lower()  # ui1
            material = parts[1].split('_')[0]  # TaskA
            task = self._convert_material_to_task(material)

            if ui and task:
                # 保存先ディレクトリ作成
                output_dir = self.image_dir / ui / task
                output_dir.mkdir(parents=True, exist_ok=True)

                # 画像を保存
                output_path = output_dir / f"{participant_id}.png"
                with zip_ref.open(image_filename) as source:
                    with open(output_path, 'wb') as target:
                        target.write(source.read())

    def _convert_material_to_task(self, material: str) -> Optional[str]:
        """
        material名（taskA/taskB）をtask番号（task1/task2）に変換

        Args:
            material: マテリアル名（taskA or taskB）

        Returns:
            タスク番号（task1 or task2）、変換できない場合はNone
        """
        material_lower = material.lower()
        if material_lower == "taska":
            return "task1"
        elif material_lower == "taskb":
            return "task2"
        return None

    def get_directory_structure(self) -> Dict[str, List[str]]:
        """
        作成されたディレクトリ構造を取得

        Returns:
            ディレクトリ構造の辞書
        """
        structure = {
            "questionnaire": {},
            "image": {},
        }

        # questionnaire構造
        for ui in ["ui1", "ui2"]:
            structure["questionnaire"][ui] = {}
            for task in ["task1", "task2"]:
                task_dir = self.questionnaire_dir / ui / task
                if task_dir.exists():
                    files = [f.name for f in task_dir.glob("*.json")]
                    structure["questionnaire"][ui][task] = sorted(files)

        # other構造
        other_files = []
        if self.other_dir.exists():
            other_files = [f.name for f in self.other_dir.glob("*.json")]
        structure["questionnaire"]["other"] = sorted(other_files)

        # image構造
        for ui in ["ui1", "ui2"]:
            structure["image"][ui] = {}
            for task in ["task1", "task2"]:
                task_dir = self.image_dir / ui / task
                if task_dir.exists():
                    files = [f.name for f in task_dir.glob("*.png")]
                    structure["image"][ui][task] = sorted(files)

        return structure

    def print_summary(self):
        """処理結果のサマリーを表示"""
        structure = self.get_directory_structure()

        print("\n" + "=" * 60)
        print("📊 実験結果の整理完了")
        print("=" * 60)

        print("\n📁 アンケートデータ (questionnaire/):")
        for ui in ["ui1", "ui2"]:
            print(f"\n  {ui.upper()}:")
            for task in ["task1", "task2"]:
                count = len(structure["questionnaire"][ui].get(task, []))
                print(f"    {task}: {count}ファイル")

        print(f"\n  その他 (other/):")
        other_count = len(structure["questionnaire"].get("other", []))
        print(f"    メタデータ・アンケート: {other_count}ファイル")

        print("\n🖼️  画像データ (image/):")
        for ui in ["ui1", "ui2"]:
            print(f"\n  {ui.upper()}:")
            for task in ["task1", "task2"]:
                count = len(structure["image"][ui].get(task, []))
                print(f"    {task}: {count}ファイル")


def main():
    """メイン実行関数"""
    print("🚀 実験結果ZIPファイルの解凍・整理を開始します\n")

    # Extractor初期化
    extractor = ExperimentResultExtractor()

    # 全ZIPファイルを処理
    results = extractor.extract_all_experiments()

    # 結果サマリー表示
    extractor.print_summary()

    # 処理結果統計
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print("\n" + "=" * 60)
    print(f"✅ 処理完了: {success_count}/{total_count}ファイル成功")
    if success_count < total_count:
        failed_files = [k for k, v in results.items() if not v]
        print(f"❌ 失敗: {', '.join(failed_files)}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
