"""
Meelo MCP Server
================

Exposes Meelo (an AI chef app) data as tools that any MCP-aware LLM client
(Claude Desktop, Claude Code, etc.) can query.

Tools exposed:
  - get_meal_plan(days)   → Pedram's upcoming meal plan
  - get_recipe(recipe_id) → Full recipe details (ingredients + steps)
  - get_taste_profile()   → Food preferences, dietary info, goals

Built on the official MCP Python SDK using the FastMCP high-level interface.
Runs over stdio transport — designed to be launched by an MCP client like
Claude Desktop, which pipes JSON messages in and out of this process.

To wire this to live Supabase data later, replace the MOCK_* dicts with
Supabase queries. The tool signatures stay the same so the client (Claude)
doesn't need any changes.
"""

from mcp.server.fastmcp import FastMCP


# ── Create the MCP server instance ──────────────────────────────────────────
# The string "meelo" is the server's name. MCP clients (Claude Desktop) use
# it to identify this server in their UI and logs.
app = FastMCP("meelo")


# ── Mock data ───────────────────────────────────────────────────────────────
# Shaped exactly like Meelo's real Supabase data so swapping to live queries
# later is a one-line change inside each tool.

MOCK_MEAL_PLAN = [
    {"day": 0, "label": "Today",     "breakfast": "Golden Turmeric Scrambled Eggs", "lunch": "Mediterranean Grain Bowl",  "dinner": "Crispy Skin Salmon with Dill Butter Lentils"},
    {"day": 1, "label": "Tomorrow",  "breakfast": "Berry Smoothie Bowl",            "lunch": "Chickpea & Halloumi Salad", "dinner": "One-Pan Chicken Thighs with Lemon Potatoes"},
    {"day": 2, "label": "Wednesday", "breakfast": "Overnight Oats with Banana",     "lunch": "Tuna Niçoise Sandwich",     "dinner": "Spicy Tofu Stir-Fry with Jasmine Rice"},
    {"day": 3, "label": "Thursday",  "breakfast": "Avocado Toast with Egg",         "lunch": "Lentil Soup with Sourdough","dinner": "Beef Tacos with Pickled Onions"},
    {"day": 4, "label": "Friday",    "breakfast": "Yogurt Granola Bowl",            "lunch": "Quinoa Tabbouleh",          "dinner": "Sheet-Pan Lemon Cod with Asparagus"},
]

MOCK_RECIPES = {
    "d0-d": {
        "id": "d0-d",
        "title": "Crispy Skin Salmon with Dill Butter Lentils",
        "cookTime": 25,
        "difficulty": "Medium",
        "mealType": "dinner",
        "ingredients": [
            {"name": "Salmon fillet", "amount": "180g per person, skin on"},
            {"name": "Green lentils", "amount": "200g, pre-cooked"},
            {"name": "Butter",        "amount": "40g"},
            {"name": "Fresh dill",    "amount": "a small bunch"},
            {"name": "Lemon",         "amount": "1, zested and juiced"},
        ],
        "steps": [
            "Season salmon skin side generously with salt. Heat a dry non-stick pan over high heat until smoking.",
            "Place salmon skin-side down and press gently with a spatula for 30 seconds to prevent curling. Cook 4 min without moving.",
            "Flip and cook 2 min more. Rest off heat.",
            "In a separate pan melt butter over medium heat until foamy. Add lentils and warm through, 3 min.",
            "Stir in lemon zest, juice, and chopped dill. Season well.",
            "Plate lentils, place salmon skin-up on top so the skin stays crispy.",
        ],
        "aiReason": "Picked because you've rated fish dishes highly — this gives you a new technique to try.",
        "chefNote": "Pat the salmon completely dry before it goes in the pan — moisture will steam instead of sear.",
    },
    "d0-b": {
        "id": "d0-b",
        "title": "Golden Turmeric Scrambled Eggs",
        "cookTime": 8,
        "difficulty": "Easy",
        "mealType": "breakfast",
        "ingredients": [
            {"name": "Eggs",                       "amount": "3 large"},
            {"name": "Butter",                     "amount": "10g"},
            {"name": "Turmeric",                   "amount": "1/4 tsp"},
            {"name": "Chives or spring onion",     "amount": "a small handful"},
            {"name": "Sourdough bread",            "amount": "1 slice, toasted"},
        ],
        "steps": [
            "Whisk eggs with a pinch of salt and turmeric until fully combined — no streaks.",
            "Melt butter in a small pan over medium-low heat.",
            "Pour in eggs and stir continuously with a silicone spatula, scraping the bottom and sides.",
            "Remove from heat when eggs are just set but still glossy — about 3-4 min.",
            "Pile onto toast and scatter over chopped chives. Eat immediately.",
        ],
        "aiReason": "Quick protein start that fits your under-15-min morning goal.",
        "chefNote": "Low and slow is the secret — keep the heat on medium-low and stir constantly. Pull off heat while still slightly wet; they finish cooking on the plate.",
    },
    "d0-l": {
        "id": "d0-l",
        "title": "Mediterranean Grain Bowl",
        "cookTime": 20,
        "difficulty": "Easy",
        "mealType": "lunch",
        "ingredients": [
            {"name": "Pearl couscous",  "amount": "150g"},
            {"name": "Cherry tomatoes", "amount": "200g, halved"},
            {"name": "Cucumber",        "amount": "1, diced"},
            {"name": "Feta cheese",     "amount": "100g, crumbled"},
            {"name": "Kalamata olives", "amount": "a small handful, pitted"},
            {"name": "Olive oil",       "amount": "3 tbsp"},
            {"name": "Lemon",           "amount": "1, juiced"},
        ],
        "steps": [
            "Bring a pot of salted water to the boil. Add couscous and simmer 8-10 min until tender. Drain and rinse under cold water.",
            "While couscous cools, chop tomatoes, cucumber, and olives.",
            "Whisk olive oil and lemon juice with salt and pepper to make the dressing.",
            "Combine everything in a large bowl. Crumble feta over the top.",
            "Toss gently and serve at room temperature — even better after 30 min in the fridge.",
        ],
        "aiReason": "Light, filling, and uses pantry staples for a quick midweek lunch.",
        "chefNote": "Don't dress the bowl until just before serving if you want it to stay crunchy.",
    },
    "d1-d": {
        "id": "d1-d",
        "title": "One-Pan Chicken Thighs with Lemon Potatoes",
        "cookTime": 45,
        "difficulty": "Easy",
        "mealType": "dinner",
        "ingredients": [
            {"name": "Chicken thighs", "amount": "4, bone-in skin-on"},
            {"name": "Baby potatoes",  "amount": "500g, halved"},
            {"name": "Lemon",          "amount": "1, sliced"},
            {"name": "Garlic",         "amount": "6 cloves, smashed"},
            {"name": "Olive oil",      "amount": "2 tbsp"},
            {"name": "Fresh thyme",    "amount": "a few sprigs"},
        ],
        "steps": [
            "Preheat oven to 200°C. Season chicken with salt and pepper.",
            "Toss potatoes with olive oil, garlic, and thyme in a roasting tray.",
            "Nestle chicken on top, skin-side up. Scatter lemon slices around.",
            "Roast for 35-40 min, basting halfway through with the pan juices.",
            "Rest 5 min before serving. Spoon pan juices over everything.",
        ],
        "aiReason": "One pan, minimal prep, and the lemon-garlic juices are the best part of the dish.",
        "chefNote": "Dry the chicken skin thoroughly before seasoning — that's what gets you crispy skin without deep frying.",
    },
    "d2-d": {
        "id": "d2-d",
        "title": "Spicy Tofu Stir-Fry with Jasmine Rice",
        "cookTime": 25,
        "difficulty": "Medium",
        "mealType": "dinner",
        "ingredients": [
            {"name": "Firm tofu",        "amount": "400g, pressed and cubed"},
            {"name": "Jasmine rice",     "amount": "200g"},
            {"name": "Tenderstem broccoli", "amount": "200g"},
            {"name": "Garlic",           "amount": "3 cloves, minced"},
            {"name": "Ginger",           "amount": "thumb-sized piece, grated"},
            {"name": "Soy sauce",        "amount": "3 tbsp"},
            {"name": "Chili oil",        "amount": "1-2 tbsp to taste"},
            {"name": "Sesame oil",       "amount": "1 tsp, to finish"},
        ],
        "steps": [
            "Start the rice — rinse, then cook according to package instructions (~15 min).",
            "Press tofu with a heavy pan for 10 min to extract water, then cube.",
            "Heat a wok or large pan over high heat. Add neutral oil. Sear tofu on all sides until golden, 5-6 min. Remove.",
            "Add garlic and ginger to the pan, stir 30 seconds. Add broccoli, stir-fry 3 min.",
            "Return tofu to the pan. Add soy sauce and chili oil. Toss to coat.",
            "Finish with sesame oil off the heat. Serve over rice.",
        ],
        "aiReason": "Plant-based dinner with serious flavor — proves you don't need meat for a satisfying stir-fry.",
        "chefNote": "Pressing tofu is the difference between rubbery and crispy. Don't skip it.",
    },
}

MOCK_TASTE_PROFILE = {
    "name": "Pedram",
    "cookingSkill": "Comfortable",
    "dietaryPreference": "no restrictions",
    "loves": ["fish", "Mediterranean cuisine", "Persian food", "spicy food", "fresh herbs"],
    "dislikes": ["cilantro", "very sweet desserts"],
    "cookingTimePreference": "under 30 minutes weekdays, 45+ minutes weekends",
    "household": 2,
    "weeklyBudget": "medium",
    "goals": ["eat more fish", "reduce food waste", "cook with what's in season"],
    "favoriteRecipes": ["Crispy Skin Salmon with Dill Butter Lentils", "Persian Saffron Chicken"],
}


# ── Tools ───────────────────────────────────────────────────────────────────
# Each @app.tool() function becomes a tool the LLM can call. The docstring
# is what the LLM reads to decide WHEN to call it — be specific.

@app.tool()
def get_meal_plan(days: int = 7) -> dict:
    """Return Pedram's planned meals (breakfast, lunch, dinner) for the next N days.

    Use this when the user asks what Pedram is cooking, what's on his meal plan,
    what's for breakfast/lunch/dinner today or tomorrow, or what the week looks like.

    Args:
        days: Number of days to return. Defaults to 7. Capped at the available plan length.
    """
    plan_slice = MOCK_MEAL_PLAN[: min(days, len(MOCK_MEAL_PLAN))]
    return {
        "user": "Pedram",
        "plan": plan_slice,
        "source": "Meelo via MCP",
    }


@app.tool()
def get_recipe(recipe_id: str) -> dict:
    """Return the full recipe (ingredients, steps, cook time, difficulty, notes) for a recipe ID.

    Use this after the user has seen a meal in the plan and wants to know how to cook it.
    Recipe IDs follow the format d{day}-{b|l|d} — e.g. d0-d is today's dinner, d1-b is
    tomorrow's breakfast.

    Args:
        recipe_id: The recipe identifier, e.g. "d0-d" or "d0-b".
    """
    recipe = MOCK_RECIPES.get(recipe_id)
    if not recipe:
        return {
            "error": f"No recipe found for ID '{recipe_id}'.",
            "available_ids": list(MOCK_RECIPES.keys()),
        }
    return recipe


@app.tool()
def get_taste_profile() -> dict:
    """Return Pedram's taste profile — preferences, dislikes, dietary info, household, goals.

    Use this when you need to personalise a recommendation or understand who you're
    cooking for. Combine with get_meal_plan to explain why a meal was picked.
    """
    return MOCK_TASTE_PROFILE


# ── Run the server ──────────────────────────────────────────────────────────
# stdio transport: the MCP client (Claude Desktop) launches this script and
# communicates with it over standard input/output. No web server needed.
if __name__ == "__main__":
    app.run()
