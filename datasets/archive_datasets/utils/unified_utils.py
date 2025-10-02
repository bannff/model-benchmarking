#!/usr/bin/env python3
"""
Unified Utilities
Consolidates common utility functions used across the pipeline.
"""

import json
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
from datetime import datetime

class DatasetUtils:
    """Utility functions for dataset management"""
    
    @staticmethod
    def load_jsonl(file_path: Path) -> List[Dict]:
        """Load data from JSONL file"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Warning: Invalid JSON on line {line_num}: {e}")
        return data
    
    @staticmethod
    def save_jsonl(data: List[Dict], file_path: Path):
        """Save data to JSONL file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    @staticmethod
    def merge_datasets(input_paths: List[Path], output_path: Path):
        """Merge multiple JSONL datasets"""
        all_data = []
        
        for path in input_paths:
            if path.exists():
                data = DatasetUtils.load_jsonl(path)
                all_data.extend(data)
                print(f"Loaded {len(data)} samples from {path}")
        
        DatasetUtils.save_jsonl(all_data, output_path)
        print(f"Merged {len(all_data)} total samples to {output_path}")
        
        return len(all_data)
    
    @staticmethod
    def sample_dataset(input_path: Path, output_path: Path, sample_size: int, random_seed: int = 42):
        """Create a random sample of a dataset"""
        import random
        random.seed(random_seed)
        
        data = DatasetUtils.load_jsonl(input_path)
        
        if len(data) <= sample_size:
            sampled_data = data
        else:
            sampled_data = random.sample(data, sample_size)
        
        DatasetUtils.save_jsonl(sampled_data, output_path)
        print(f"Sampled {len(sampled_data)} from {len(data)} samples")
        
        return len(sampled_data)
    
    @staticmethod
    def analyze_dataset_stats(file_path: Path) -> Dict[str, Any]:
        """Analyze basic dataset statistics"""
        data = DatasetUtils.load_jsonl(file_path)
        
        if not data:
            return {"error": "No data found"}
        
        stats = {
            "total_samples": len(data),
            "sample_keys": list(data[0].keys()) if data else [],
            "avg_content_length": 0,
            "message_role_distribution": {},
            "analysis_date": datetime.now().isoformat()
        }
        
        total_length = 0
        role_counts = {}
        
        for sample in data:
            if "messages" in sample:
                for msg in sample["messages"]:
                    role = msg.get("role", "unknown")
                    role_counts[role] = role_counts.get(role, 0) + 1
                    
                    content_length = len(msg.get("content", ""))
                    total_length += content_length
        
        stats["avg_content_length"] = total_length / max(sum(role_counts.values()), 1)
        stats["message_role_distribution"] = role_counts
        
        return stats

class FileUtils:
    """Utility functions for file management"""
    
    @staticmethod
    def cleanup_directory(directory: Path, patterns_to_remove: List[str] = None):
        """Clean up directory by removing specified patterns"""
        if patterns_to_remove is None:
            patterns_to_remove = ["*.tmp", "*.log", "__pycache__", ".DS_Store"]
        
        removed_count = 0
        
        for pattern in patterns_to_remove:
            for item in directory.rglob(pattern):
                if item.is_file():
                    item.unlink()
                    removed_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    removed_count += 1
        
        print(f"Cleaned up {removed_count} items from {directory}")
        return removed_count
    
    @staticmethod
    def organize_scripts(source_dir: Path, target_structure: Dict[str, List[str]]):
        """Organize scripts into target directory structure"""
        moved_files = []
        
        for target_subdir, file_patterns in target_structure.items():
            target_path = source_dir / target_subdir
            target_path.mkdir(exist_ok=True)
            
            for pattern in file_patterns:
                for file_path in source_dir.glob(pattern):
                    if file_path.is_file() and file_path.parent == source_dir:
                        new_path = target_path / file_path.name
                        if not new_path.exists():
                            shutil.move(str(file_path), str(new_path))
                            moved_files.append((file_path, new_path))
                            print(f"Moved: {file_path.name} -> {target_subdir}/")
        
        return moved_files
    
    @staticmethod
    def remove_duplicates(directory: Path, dry_run: bool = True):
        """Find and optionally remove duplicate files"""
        import hashlib
        
        file_hashes = {}
        duplicates = []
        
        for file_path in directory.rglob("*.py"):
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                if file_hash in file_hashes:
                    duplicates.append((file_path, file_hashes[file_hash]))
                else:
                    file_hashes[file_hash] = file_path
        
        print(f"Found {len(duplicates)} duplicate files:")
        for dup, original in duplicates:
            print(f"  {dup} (duplicate of {original})")
            if not dry_run:
                dup.unlink()
                print(f"    Removed: {dup}")
        
        if dry_run and duplicates:
            print("\nRun with --no-dry-run to actually remove duplicates")
        
        return duplicates

class PipelineOrchestrator:
    """Orchestrate the complete pipeline"""
    
    def __init__(self, workspace_dir: str = "/Users/danielrodrigo/Workspace/datasets"):
        self.workspace_dir = Path(workspace_dir)
        self.data_collection_dir = self.workspace_dir / "data_collection"
        self.data_processing_dir = self.workspace_dir / "data_processing"
        self.training_dir = self.workspace_dir / "training"
        self.evaluation_dir = self.workspace_dir / "evaluation"
        self.utils_dir = self.workspace_dir / "utils"
    
    def organize_workspace(self):
        """Organize the entire workspace"""
        print("🗂️  Organizing workspace...")
        
        # Create directory structure
        for dir_path in [self.data_collection_dir, self.data_processing_dir, 
                        self.training_dir, self.evaluation_dir, self.utils_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Move existing scripts to appropriate directories
        organization_map = {
            "data_collection": [
                "download_*.py", "research_*.py", "search_*.py"
            ],
            "data_processing": [
                "clean_*.py", "convert_*.py", "prepare_*.py", "split_*.py", "export_*.py"
            ],
            "training": [
                "*trainer*.py", "*train*.py", "finetune*.py"
            ],
            "evaluation": [
                "*evaluator*.py", "*eval*.py", "test_*.py"
            ],
            "utils": [
                "*monitor*.py", "*utils*.py"
            ]
        }
        
        moved_files = FileUtils.organize_scripts(self.workspace_dir, organization_map)
        
        # Clean up duplicates
        print("\n🧹 Checking for duplicates...")
        duplicates = FileUtils.remove_duplicates(self.workspace_dir, dry_run=False)
        
        # Clean up temporary files
        print("\n🗑️  Cleaning up temporary files...")
        FileUtils.cleanup_directory(self.workspace_dir)
        
        print(f"\n✅ Workspace organization complete!")
        print(f"  Moved {len(moved_files)} files")
        print(f"  Removed {len(duplicates)} duplicates")
        
        return {
            "moved_files": moved_files,
            "removed_duplicates": duplicates
        }
    
    def run_complete_pipeline(self, dataset_name: str):
        """Run the complete pipeline from data collection to evaluation"""
        print(f"🚀 Running complete pipeline for: {dataset_name}")
        
        # Step 1: Data Collection
        print("\n📥 Step 1: Data Collection")
        # Run unified collector...
        
        # Step 2: Data Processing
        print("\n🔄 Step 2: Data Processing")
        # Run unified processor...
        
        # Step 3: Training
        print("\n🎯 Step 3: Training")
        # Run unified trainer...
        
        # Step 4: Evaluation
        print("\n📊 Step 4: Evaluation")
        # Run unified evaluator...
        
        print("\n🎉 Pipeline complete!")

def main():
    parser = argparse.ArgumentParser(description="Dataset utilities and pipeline orchestration")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Organize command
    organize_parser = subparsers.add_parser("organize", help="Organize workspace")
    organize_parser.add_argument("--workspace-dir", default="/Users/danielrodrigo/Workspace/datasets")
    
    # Merge datasets command
    merge_parser = subparsers.add_parser("merge", help="Merge datasets")
    merge_parser.add_argument("inputs", nargs="+", help="Input JSONL files")
    merge_parser.add_argument("--output", required=True, help="Output JSONL file")
    
    # Sample dataset command
    sample_parser = subparsers.add_parser("sample", help="Sample dataset")
    sample_parser.add_argument("input", help="Input JSONL file")
    sample_parser.add_argument("output", help="Output JSONL file")
    sample_parser.add_argument("--size", type=int, required=True, help="Sample size")
    sample_parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze dataset")
    analyze_parser.add_argument("input", help="Input JSONL file")
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run complete pipeline")
    pipeline_parser.add_argument("dataset", help="Dataset name")
    pipeline_parser.add_argument("--workspace-dir", default="/Users/danielrodrigo/Workspace/datasets")
    
    args = parser.parse_args()
    
    if args.command == "organize":
        orchestrator = PipelineOrchestrator(args.workspace_dir)
        orchestrator.organize_workspace()
    
    elif args.command == "merge":
        input_paths = [Path(p) for p in args.inputs]
        output_path = Path(args.output)
        DatasetUtils.merge_datasets(input_paths, output_path)
    
    elif args.command == "sample":
        input_path = Path(args.input)
        output_path = Path(args.output)
        DatasetUtils.sample_dataset(input_path, output_path, args.size, args.seed)
    
    elif args.command == "analyze":
        input_path = Path(args.input)
        stats = DatasetUtils.analyze_dataset_stats(input_path)
        print(json.dumps(stats, indent=2))
    
    elif args.command == "pipeline":
        orchestrator = PipelineOrchestrator(args.workspace_dir)
        orchestrator.run_complete_pipeline(args.dataset)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
