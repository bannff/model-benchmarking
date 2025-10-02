#!/usr/bin/env python3
"""
COMPREHENSIVE DATASET QUALITY ANALYZER
Advanced validation and quality assessment for cybersecurity training datasets
"""

import json
import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set
from collections import Counter, defaultdict
import argparse
from datetime import datetime
import statistics
import hashlib

class DatasetQualityAnalyzer:
    def __init__(self):
        # Define fake tool patterns that contaminate datasets
        self.fake_tools = [
            'vulnerability_scanner',
            'threat_intel_lookup', 
            'nmap_scan',
            'dns_lookup',
            'ip_geolocation',
            'subdomain_enum',
            'port_scanner',
            'ssl_checker',
            'whois_lookup',
            'cve_search',
            'exploit_db_search',
            'network_monitor',
            'firewall_check',
            'malware_analysis',
            'file_hash_checker'
        ]
        
        # High-quality cybersecurity indicators
        self.quality_indicators = {
            'technical_terms': [
                'vulnerability', 'exploit', 'malware', 'firewall', 'encryption',
                'authentication', 'authorization', 'penetration', 'reconnaissance',
                'phishing', 'ransomware', 'backdoor', 'trojan', 'rootkit',
                'botnet', 'zero-day', 'buffer overflow', 'sql injection',
                'cross-site scripting', 'xss', 'csrf', 'mitm', 'dns poisoning',
                'arp spoofing', 'social engineering', 'threat modeling',
                'risk assessment', 'incident response', 'forensics',
                'cryptography', 'hashing', 'digital signature', 'certificate',
                'pki', 'ids', 'ips', 'siem', 'dlp', 'vpn', 'tls', 'ssl'
            ],
            'security_frameworks': [
                'nist', 'iso 27001', 'owasp', 'sans', 'cis', 'mitre att&ck',
                'stride', 'dread', 'octave', 'fair', 'coso', 'cobit'
            ],
            'programming_security': [
                'secure coding', 'code review', 'static analysis', 'dynamic analysis',
                'fuzzing', 'sanitization', 'validation', 'parameterized queries',
                'prepared statements', 'input validation', 'output encoding'
            ]
        }
        
        # Low-quality indicators
        self.garbage_indicators = [
            'lorem ipsum', 'test test test', 'example example',
            'placeholder', 'dummy data', 'sample text',
            'foo bar', 'hello world', 'this is a test'
        ]
        
        self.stats = {
            'total_entries': 0,
            'fake_tool_contaminated': 0,
            'high_quality_entries': 0,
            'medium_quality_entries': 0,
            'low_quality_entries': 0,
            'duplicate_entries': 0,
            'empty_entries': 0,
            'tool_usage_counts': Counter(),
            'quality_scores': [],
            'conversation_lengths': [],
            'duplicates_found': set(),
            'content_analysis': defaultdict(int)
        }

    def analyze_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single dataset entry for quality metrics"""
        analysis = {
            'has_fake_tools': False,
            'fake_tools_found': [],
            'quality_score': 0.0,
            'conversation_length': 0,
            'is_duplicate': False,
            'content_hash': '',
            'cybersec_terms_count': 0,
            'garbage_indicators_count': 0,
            'is_english': True,
            'has_code': False,
            'is_coherent': True
        }
        
        # Extract conversation text
        conversation_text = ""
        if 'conversations' in entry:
            for conv in entry['conversations']:
                if 'value' in conv:
                    conversation_text += conv['value'] + " "
        elif 'messages' in entry:
            for msg in entry['messages']:
                if 'content' in msg:
                    conversation_text += msg['content'] + " "
        else:
            # Handle other formats
            conversation_text = str(entry)
        
        conversation_text = conversation_text.lower()
        analysis['conversation_length'] = len(conversation_text.split())
        
        # Check for duplicate content
        analysis['content_hash'] = hashlib.md5(conversation_text.encode()).hexdigest()
        if analysis['content_hash'] in self.stats['duplicates_found']:
            analysis['is_duplicate'] = True
            self.stats['duplicate_entries'] += 1
        else:
            self.stats['duplicates_found'].add(analysis['content_hash'])
        
        # Check for fake tools
        for tool in self.fake_tools:
            if tool in conversation_text:
                analysis['has_fake_tools'] = True
                analysis['fake_tools_found'].append(tool)
                self.stats['tool_usage_counts'][tool] += 1
        
        # Count cybersecurity terms
        for category, terms in self.quality_indicators.items():
            for term in terms:
                if term in conversation_text:
                    analysis['cybersec_terms_count'] += conversation_text.count(term)
        
        # Count garbage indicators
        for garbage in self.garbage_indicators:
            if garbage in conversation_text:
                analysis['garbage_indicators_count'] += conversation_text.count(garbage)
        
        # Check for code presence
        if any(pattern in conversation_text for pattern in ['def ', 'class ', 'import ', 'function', 'var ', 'const ']):
            analysis['has_code'] = True
        
        # Calculate quality score
        quality_score = 0.0
        
        # Positive factors
        quality_score += min(analysis['cybersec_terms_count'] * 2, 20)  # Max 20 points
        quality_score += min(analysis['conversation_length'] / 10, 15)  # Max 15 points for length
        if analysis['has_code']:
            quality_score += 10
        if not analysis['has_fake_tools']:
            quality_score += 25  # Major bonus for no fake tools
        
        # Negative factors
        quality_score -= analysis['garbage_indicators_count'] * 10
        quality_score -= len(analysis['fake_tools_found']) * 15
        if analysis['is_duplicate']:
            quality_score -= 30
        
        # Coherence check (simple heuristic)
        repeated_phrases = self._check_repetition(conversation_text)
        if repeated_phrases > 3:
            analysis['is_coherent'] = False
            quality_score -= 20
        
        analysis['quality_score'] = max(0, min(100, quality_score))
        
        return analysis

    def _check_repetition(self, text: str) -> int:
        """Check for excessive repetition in text"""
        words = text.split()
        if len(words) < 10:
            return 0
        
        # Count 3-word phrases
        phrases = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        phrase_counts = Counter(phrases)
        
        # Count phrases that appear more than once
        repeated = sum(1 for count in phrase_counts.values() if count > 1)
        return repeated

    def analyze_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Analyze entire dataset for quality metrics"""
        print(f"🔍 Analyzing dataset: {dataset_path}")
        
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    analysis = self.analyze_entry(entry)
                    
                    self.stats['total_entries'] += 1
                    self.stats['quality_scores'].append(analysis['quality_score'])
                    self.stats['conversation_lengths'].append(analysis['conversation_length'])
                    
                    if analysis['has_fake_tools']:
                        self.stats['fake_tool_contaminated'] += 1
                    
                    # Classify quality
                    if analysis['quality_score'] >= 70:
                        self.stats['high_quality_entries'] += 1
                    elif analysis['quality_score'] >= 40:
                        self.stats['medium_quality_entries'] += 1
                    else:
                        self.stats['low_quality_entries'] += 1
                    
                    # Progress indicator
                    if line_num % 1000 == 0:
                        print(f"Processed {line_num:,} entries...")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error at line {line_num}: {e}")
                    continue
                except Exception as e:
                    print(f"❌ Error processing line {line_num}: {e}")
                    continue
        
        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        if not self.stats['quality_scores']:
            return {"error": "No valid entries found"}
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overview': {
                'total_entries': self.stats['total_entries'],
                'contamination_rate': round(self.stats['fake_tool_contaminated'] / self.stats['total_entries'] * 100, 2),
                'duplicate_rate': round(self.stats['duplicate_entries'] / self.stats['total_entries'] * 100, 2),
                'high_quality_rate': round(self.stats['high_quality_entries'] / self.stats['total_entries'] * 100, 2)
            },
            'quality_distribution': {
                'high_quality': self.stats['high_quality_entries'],
                'medium_quality': self.stats['medium_quality_entries'],
                'low_quality': self.stats['low_quality_entries']
            },
            'quality_metrics': {
                'average_score': round(statistics.mean(self.stats['quality_scores']), 2),
                'median_score': round(statistics.median(self.stats['quality_scores']), 2),
                'score_std_dev': round(statistics.stdev(self.stats['quality_scores']), 2),
                'min_score': min(self.stats['quality_scores']),
                'max_score': max(self.stats['quality_scores'])
            },
            'conversation_stats': {
                'average_length': round(statistics.mean(self.stats['conversation_lengths']), 2),
                'median_length': round(statistics.median(self.stats['conversation_lengths']), 2),
                'total_words': sum(self.stats['conversation_lengths'])
            },
            'contamination_details': {
                'fake_tools_found': dict(self.stats['tool_usage_counts'].most_common()),
                'most_common_fake_tool': self.stats['tool_usage_counts'].most_common(1)[0] if self.stats['tool_usage_counts'] else None
            },
            'recommendations': self._generate_recommendations()
        }
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        contamination_rate = self.stats['fake_tool_contaminated'] / self.stats['total_entries'] * 100
        if contamination_rate > 10:
            recommendations.append(f"🚨 HIGH CONTAMINATION: {contamination_rate:.1f}% of entries contain fake tools - aggressive cleaning required")
        
        duplicate_rate = self.stats['duplicate_entries'] / self.stats['total_entries'] * 100
        if duplicate_rate > 5:
            recommendations.append(f"📄 DUPLICATES DETECTED: {duplicate_rate:.1f}% duplicates found - deduplication recommended")
        
        high_quality_rate = self.stats['high_quality_entries'] / self.stats['total_entries'] * 100
        if high_quality_rate < 30:
            recommendations.append(f"📉 LOW QUALITY: Only {high_quality_rate:.1f}% high-quality entries - consider sourcing better data")
        
        avg_score = statistics.mean(self.stats['quality_scores'])
        if avg_score < 50:
            recommendations.append(f"⚠️ POOR AVERAGE QUALITY: Score {avg_score:.1f}/100 - extensive cleaning required")
        
        if not recommendations:
            recommendations.append("✅ Dataset quality looks good! Minor cleaning may still be beneficial.")
        
        return recommendations

    def find_external_datasets(self, search_paths: List[str]) -> List[str]:
        """Search for additional cybersecurity datasets in common locations"""
        found_datasets = []
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
                
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith(('.jsonl', '.json', '.txt', '.csv')):
                        if any(keyword in file.lower() for keyword in ['cybersec', 'security', 'hack', 'vuln', 'threat', 'heimdall']):
                            full_path = os.path.join(root, file)
                            if os.path.getsize(full_path) > 1024:  # At least 1KB
                                found_datasets.append(full_path)
        
        return found_datasets

def main():
    parser = argparse.ArgumentParser(description='Analyze dataset quality for cybersecurity training')
    parser.add_argument('dataset_path', help='Path to dataset file (.jsonl)')
    parser.add_argument('--output', '-o', help='Output report file (JSON)', default='quality_report.json')
    parser.add_argument('--search-external', '-s', action='store_true', help='Search for external datasets')
    parser.add_argument('--search-paths', nargs='+', default=['/Users/danielrodrigo/Downloads', '/Users/danielrodrigo/Desktop', '/Users/danielrodrigo/Documents'], help='Paths to search for external datasets')
    
    args = parser.parse_args()
    
    analyzer = DatasetQualityAnalyzer()
    
    # Search for external datasets if requested
    if args.search_external:
        print("🔍 Searching for external datasets...")
        external_datasets = analyzer.find_external_datasets(args.search_paths)
        if external_datasets:
            print(f"📁 Found {len(external_datasets)} potential datasets:")
            for dataset in external_datasets:
                print(f"  - {dataset}")
        else:
            print("❌ No external datasets found")
        print()
    
    # Analyze main dataset
    try:
        report = analyzer.analyze_dataset(args.dataset_path)
        
        # Save report
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 DATASET QUALITY REPORT")
        print("="*60)
        print(f"Total Entries: {report['overview']['total_entries']:,}")
        print(f"Contamination Rate: {report['overview']['contamination_rate']}%")
        print(f"Duplicate Rate: {report['overview']['duplicate_rate']}%")
        print(f"High Quality Rate: {report['overview']['high_quality_rate']}%")
        print(f"Average Quality Score: {report['quality_metrics']['average_score']}/100")
        print()
        
        print("🎯 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        
        print(f"\n📄 Full report saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error analyzing dataset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
