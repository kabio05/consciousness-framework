class ReportGenerator:
    def __init__(self):
        pass
    
    def generate_summary(self, consciousness_profile):
        """Generate a text summary of consciousness assessment results"""
        if not consciousness_profile:
            return "No assessment results available."
        
        summary = f"Consciousness Assessment for {consciousness_profile.model_name}\n"
        summary += "=" * 50 + "\n\n"
        summary += f"Overall Score: {consciousness_profile.overall_score:.3f}/1.0\n\n"
        
        if hasattr(consciousness_profile, 'trait_scores') and consciousness_profile.trait_scores:
            summary += "Trait Scores:\n"
            for trait, score in consciousness_profile.trait_scores.items():
                if trait != 'overall_consciousness':
                    summary += f"  - {trait.replace('_', ' ').title()}: {score:.3f}\n"
        
        if consciousness_profile.strengths:
            summary += f"\nStrengths:\n"
            for strength in consciousness_profile.strengths:
                summary += f"  • {strength}\n"
        
        if consciousness_profile.weaknesses:
            summary += f"\nWeaknesses:\n"
            for weakness in consciousness_profile.weaknesses:
                summary += f"  • {weakness}\n"
        
        return summary
    
    def create_visualizations(self, scores):
        """Create basic visualization data (for web interface)"""
        return {
            "type": "radar_chart",
            "data": scores,
            "labels": list(scores.keys()) if isinstance(scores, dict) else []
        }