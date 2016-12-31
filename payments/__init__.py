BASIC_MONTHLY = 'basic_monthly'
BASIC_YEARLY = 'basic_yearly'
TEAM_MONTHLY = 'team_monthly'
TEAM_YEARLY = 'team_yearly'
FAMILY_MONTHLY = 'family_monthly'
FAMILY_YEARLY = 'family_yearly'

PLANS = {
    BASIC_MONTHLY: {
        'is_active': True,
        'stripe_id': 'basic_monthly',
        'stripe_cost': 500,
        'usd_cost': '5.00',
        'collaborators': 1,
        'name': 'Basic Monthly Subscription'
    },
    BASIC_YEARLY: {
        'is_active': True,
        'stripe_id': 'basic_yearly',
        'stripe_cost': 5000,
        'usd_cost': '50.00',
        'collaborators': 1,
        'name': 'Basic Yearly Subscription'
    },
    FAMILY_MONTHLY: {
        'is_active': True,
        'stripe_id': 'family_monthly',
        'stripe_cost': 1000,
        'usd_cost': '10.00',
        'collaborators': 5,
        'name': 'Family Monthly Subscription'
    },
    FAMILY_YEARLY: {
        'is_active': True,
        'stripe_id': 'family_yearly',
        'stripe_cost': 10000,
        'usd_cost': '100.00',
        'collaborators': 5,
        'name': 'Family Yearly Subscription'
    },
    TEAM_MONTHLY: {
        'is_active': True,
        'stripe_id': 'team_monthly',
        'stripe_cost': 2000,
        'usd_cost': '20.00',
        'collaborators': 20,
        'name': 'Team Monthly Subscription'
    },
    TEAM_YEARLY: {
        'is_active': True,
        'stripe_id': 'team_yearly',
        'stripe_cost': 20000,
        'usd_cost': '200.00',
        'collaborators': 20,
        'name': 'Team Yearly Subscription'
    },
}

PLAN_CHOICES = (
    (PLANS[plan]['stripe_id'], PLANS[plan]['name']) for plan in PLANS
)