"""
main.py
-------
Entry point for CrodlinOutreachAgent.
Handles user input, niche selection, and pipeline trigger.

Usage:
  uv run main.py                          # Interactive mode
  uv run main.py --mode outreach          # With args
  uv run main.py --mode feedback          # Feedback loop
"""

import asyncio
import argparse
import uuid
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from utils.logger import logger
from config.settings import settings
from agents.research.agent import NicheSuggester, NicheResearchAgent
from agents.research.schema import ResearchAgentInput


console = Console()


def print_banner():
    """Print welcome banner."""
    console.print(Panel.fit(
        "[bold cyan]CrodlinOutreachAgent[/bold cyan]\n"
        "[dim]AI-Powered Cold Email Outreach System[/dim]\n"
        "[dim]by Crodlin Technology, Mumbai[/dim]",
        border_style="cyan"
    ))


async def get_user_inputs() -> dict:
    """
    Interactive input collection.
    Returns dict with all user inputs.
    """
    console.print("\n[bold yellow]Step 1 of 3 — Your Goal[/bold yellow]")
    user_goal = Prompt.ask(
        "[cyan]What is your outreach goal?[/cyan]\n"
        "[dim](e.g. 'I want to find clients for my software agency', "
        "'I am looking for a job in AI startups')[/dim]\n"
        "> "
    ).strip()

    console.print("\n[bold yellow]Step 2 of 3 — About You[/bold yellow]")
    about_user = Prompt.ask(
        "[cyan]Tell us about yourself / your service[/cyan]\n"
        "[dim](e.g. 'We build custom software, AI tools, and mobile apps "
        "for Indian SMBs. Our stack is Python, FastAPI, Next.js, Flutter')[/dim]\n"
        "> "
    ).strip()

    console.print("\n[bold yellow]Step 3 of 3 — Target Niche[/bold yellow]")
    niche_input = Prompt.ask(
        "[cyan]Do you have a specific niche in mind?[/cyan]\n"
        "[dim](Press Enter to let AI suggest niches based on your goal)[/dim]\n"
        "> ",
        default=""
    ).strip()

    location = Prompt.ask(
        "\n[cyan]Target location?[/cyan]",
        default="Mumbai, India"
    ).strip()

    outreach_type = Prompt.ask(
        "\n[cyan]Outreach type?[/cyan]",
        choices=["service", "job", "freelance"],
        default="service"
    )

    return {
        "user_goal": user_goal,
        "about_user": about_user,
        "niche_input": niche_input,
        "location": location,
        "outreach_type": outreach_type,
    }


async def handle_niche_selection(
    niche_input: str,
    user_goal: str,
    about_user: str
) -> list[str]:
    """
    If niche provided → use it directly.
    If not → AI suggests 5 niches → user selects.
    Returns list of confirmed niches.
    """
    if niche_input:
        console.print(f"\n[green]✓ Using niche:[/green] {niche_input}")
        return [niche_input]

    # AI niche suggestion
    console.print("\n[bold cyan]🤖 AI is analyzing your goal and suggesting niches...[/bold cyan]")

    suggester = NicheSuggester()
    suggestions = await suggester.suggest(user_goal, about_user)

    # Display suggestions table
    table = Table(title="AI-Suggested Niches", border_style="cyan")
    table.add_column("#", style="bold yellow", width=3)
    table.add_column("Niche", style="bold white")
    table.add_column("Why it fits", style="dim")
    table.add_column("Market", style="green")

    for i, s in enumerate(suggestions, 1):
        table.add_row(
            str(i),
            s.niche,
            s.reasoning[:60] + "..." if len(s.reasoning) > 60 else s.reasoning,
            s.estimated_market_size
        )

    console.print(table)

    # Let user select
    console.print("\n[dim]Enter numbers separated by comma (e.g. 1,3,5) or 'all'[/dim]")
    selection = Prompt.ask("[cyan]Select niches to target[/cyan]", default="all")

    if selection.strip().lower() == "all":
        selected = suggestions
    else:
        indices = [int(x.strip()) - 1 for x in selection.split(",") if x.strip().isdigit()]
        selected = [suggestions[i] for i in indices if 0 <= i < len(suggestions)]

    confirmed_niches = [s.niche for s in selected]
    console.print(f"\n[green]✓ Selected niches:[/green] {', '.join(confirmed_niches)}")

    return confirmed_niches


async def run_outreach(args=None) -> None:
    """Full outreach pipeline."""
    print_banner()

    # Get inputs
    if args and args.niche:
        inputs = {
            "user_goal": args.goal or "Find clients for my software agency",
            "about_user": args.about or "Software development agency",
            "niche_input": args.niche,
            "location": args.location or settings.DEFAULT_LOCATION,
            "outreach_type": args.type or "service",
        }
    else:
        inputs = await get_user_inputs()

    # Niche selection
    niches = await handle_niche_selection(
        inputs["niche_input"],
        inputs["user_goal"],
        inputs["about_user"]
    )

    # Confirm before starting
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Niches    : {', '.join(niches)}")
    console.print(f"  Location  : {inputs['location']}")
    console.print(f"  Type      : {inputs['outreach_type']}")
    console.print(f"  Businesses: {10 * len(niches)} total ({10} per niche)")

    if not Confirm.ask("\n[cyan]Start research?[/cyan]", default=True):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    from db.database import async_session_maker
    from db.models import Campaign, CampaignStatus
    import uuid

    # Create master campaign
    campaign_id = str(uuid.uuid4())
    
    async with async_session_maker() as session:
        campaign_record = Campaign(
            id=uuid.UUID(campaign_id),
            name=f"Outreach - {inputs['outreach_type']}",
            niche="Multiple Niches",
            target_location=inputs["location"],
            status=CampaignStatus.running
        )
        session.add(campaign_record)
        await session.commit()

    # Run research for each niche
    research_agent = NicheResearchAgent()

    for niche in niches:
        console.print(f"\n[bold cyan]🔍 Researching:[/bold cyan] {niche}")

        try:
            result = await research_agent.run(ResearchAgentInput(
                campaign_id=campaign_id,
                niche=niche,
                location=inputs["location"],
                target_count=10
            ))

            console.print(f"[green]✓ Found {result.total_found} businesses[/green]")
            console.print(f"[dim]  Pain points: {len(result.niche_research.pain_points)} identified[/dim]")

            # Show businesses found
            table = Table(border_style="dim")
            table.add_column("Business", style="white")
            table.add_column("Website", style="cyan")
            table.add_column("Location", style="dim")

            for biz in result.businesses[:5]:  # Show first 5
                table.add_row(
                    biz.name,
                    biz.website or "—",
                    biz.city or biz.location or "—"
                )

            console.print(table)
            if len(result.businesses) > 5:
                console.print(f"[dim]  ...and {len(result.businesses) - 5} more saved to DB[/dim]")

        except Exception as e:
            logger.error(f"Research failed for niche '{niche}': {e}")
            console.print(f"[red]✗ Research failed for {niche}: {e}[/red]")

    console.print("\n[bold green]✓ Research phase complete![/bold green]")
    console.print("[dim]Next: Contact finder will extract emails from discovered businesses.[/dim]")


async def run_feedback() -> None:
    """Run feedback/learning pipeline."""
    console.print("[bold cyan]Running feedback analysis...[/bold cyan]")
    # TODO: Week 8 — Feedback Agent
    logger.info("Feedback pipeline — not yet implemented")
    console.print("[yellow]Feedback agent coming in Week 8.[/yellow]")


def parse_args():
    parser = argparse.ArgumentParser(
        description="CrodlinOutreachAgent — AI Cold Email Outreach"
    )
    parser.add_argument(
        "--mode",
        choices=["outreach", "feedback", "warmup"],
        default="outreach"
    )
    parser.add_argument("--niche", type=str, default="")
    parser.add_argument("--location", type=str, default="")
    parser.add_argument("--type", choices=["service", "job", "freelance"], default="service")
    parser.add_argument("--goal", type=str, default="")
    parser.add_argument("--about", type=str, default="")
    return parser.parse_args()


async def main():
    args = parse_args()

    if args.mode == "outreach":
        await run_outreach(args if args.niche else None)
    elif args.mode == "feedback":
        await run_feedback()
    elif args.mode == "warmup":
        console.print("[yellow]Warmup module coming soon.[/yellow]")


if __name__ == "__main__":
    asyncio.run(main())