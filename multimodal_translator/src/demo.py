import argparse
from pathlib import Path
import textwrap

from src.agents.visual_describer import VisualDescriberAgent
from src.agents.audio_producer import AudioProducerAgent
from src.agents.sign_language_agent import SignLanguageAgent
from src.agents.visual_simplifier import VisualSimplifierAgent
from src.agents.content_analyzer import ContentAnalyzerAgent
from src.agents.quality_checker import QualityCheckerAgent


def run_image_to_audio(args):
    img_path = args.image_path
    detail = args.detail_level

    print(f"\n[Image -> Audio] Processing image: {img_path} (detail={detail})")

    visual_agent = VisualDescriberAgent()
    audio_agent = AudioProducerAgent()
    qc_agent = QualityCheckerAgent()

    # 1) Image -> text description
    description = visual_agent.describe_image(img_path, detail_level=detail)
    print("\n=== Image -> text description ===")
    print(textwrap.fill(description, width=80))

    # 2) Quality review
    review = qc_agent.review_description(description)
    print("\n=== Quality review ===")
    print(f"Readability level : {review['readability_level']}")
    print(f"Issues            : {review['issues']}")
    print(f"Suggestions       : {review['suggestions']}")

    # 3) Text -> speech
    audio_path = audio_agent.synthesize(description, basename="image_description")
    print("\n=== Text -> speech ===")
    print(f"\nAudio file saved at: {audio_path.resolve()}")


def run_text_to_sign(args):
    text = args.text
    print("\n[Text -> Sign] Input text:")
    print(textwrap.fill(text, width=80))

    sign_agent = SignLanguageAgent()
    result = sign_agent.text_to_sign_description(text)

    print("\n=== Simplified English ===")
    print(textwrap.fill(result["simplified_english"], width=80))

    print("\n=== ASL Gloss ===")
    print(result["asl_gloss"])

    print("\n=== Body & Face Notes ===")
    print(textwrap.fill(result["body_and_face_notes"], width=80))


def run_text_to_visual(args):
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    else:
        text = args.text

    print("\n[Complex Text -> Visual] Input:")
    print(textwrap.shorten(text, width=300, placeholder="..."))

    visual_agent = VisualSimplifierAgent()

    plan = visual_agent.plan_diagram(text)

    print("\n=== Diagram Plan ===")
    print(f"Title: {plan['short_title']}\n")

    print("Diagram description:")
    print(textwrap.fill(plan["diagram_description"], width=80))

    print("\nLabels / nodes:")
    labels = plan["labels_and_nodes"]

    if isinstance(labels, dict):
        labels = ", ".join(f"{k}: {v}" for k, v in labels.items())
    elif isinstance(labels, list):
        labels = ", ".join(labels)
    print(textwrap.fill(labels, width=80))

    print("\nSimple explanation:")
    print(textwrap.fill(plan["simple_explanation"], width=80))

    if args.generate_image:
        print("\nGenerating diagram image with GPT Image...")
        img_path = visual_agent.generate_diagram_image(
            prompt=plan["diagram_description"],
            filename="diagram.png",
        )
        print(f"Diagram image saved at: {img_path.resolve()}")


def run_analyzer_demo(args):
    user_goal = args.goal
    has_image = bool(args.image_path)
    has_text = bool(args.text)

    analyzer = ContentAnalyzerAgent()
    result = analyzer.analyze(
        user_goal=user_goal,
        has_image=has_image,
        has_text=has_text,
    )

    print("\n=== Content Analyzer ===")
    print(f"Content type : {result['content_type']}")
    print(f"Recommended pipelines : {result['recommended_pipelines']}")
    print(f"Notes : {result['notes']}")


def main():
    parser = argparse.ArgumentParser(
        description="Multimodal Accessibility Translator demo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1) Image -> Audio
    p_img = subparsers.add_parser(
        "image_to_audio", help="Describe an image and generate audio."
    )
    p_img.add_argument("image_path", type=str, help="Path to input image")
    p_img.add_argument(
        "--detail-level",
        choices=["brief", "standard", "detailed"],
        default="standard",
        help="Description detail level",
    )
    p_img.set_defaults(func=run_image_to_audio)

    # 2) Text -> Sign language description
    p_sign = subparsers.add_parser(
        "text_to_sign", help="Convert text to an ASL-style sign description."
    )
    p_sign.add_argument("text", type=str, help="Input sentence")
    p_sign.set_defaults(func=run_text_to_sign)

    # 3) Complex text -> visual
    p_vis = subparsers.add_parser(
        "text_to_visual", help="Convert complex text into a visual explanation."
    )
    group = p_vis.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Text directly on the CLI")
    group.add_argument("--text-file", type=str, help="Path to text file")
    p_vis.add_argument(
        "--generate-image",
        action="store_true",
        help="Also call GPT Image to generate an actual diagram PNG.",
    )
    p_vis.set_defaults(func=run_text_to_visual)

    # 4) Analyzer-only demo (agentic planning)
    p_ana = subparsers.add_parser(
        "analyze", help="Run only the content analyzer agent."
    )
    p_ana.add_argument(
        "--goal",
        type=str,
        required=True,
        help="User's accessibility goal, e.g. 'Help a blind user understand this slide'.",
    )
    p_ana.add_argument("--image-path", type=str, help="Optional image path")
    p_ana.add_argument("--text", type=str, help="Optional text input")
    p_ana.set_defaults(func=run_analyzer_demo)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
