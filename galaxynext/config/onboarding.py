from erpnext.config.onboarding import get_onboarding_steps as erpnext_onboarding

def get_onboarding_steps():
    steps = erpnext_onboarding()
    if steps and "title" in steps[0]:
        steps[0]["title"] = "Let's begin your journey with GalaxyNext"
    return steps

