import os
import stripe
from dotenv import load_dotenv
import warnings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        warnings.warn(error_msg)

def main():
    stripe.api_key = get_env_variable("STRIPE_TEST_KEY")
    plans = stripe.Plan.list()
    stripe.api_key = get_env_variable("STRIPE_LIVE_KEY")
    for plan in plans['data']:
        try:
            plan = stripe.Plan.retrieve(plan['id'])
            print("Plan {} already exists on LIVE".format(plan['id']))
        except stripe.error.InvalidRequestError:
            stripe.Plan.create(
                id=plan['id'],
                amount=plan['amount'],
                currency=plan['currency'],
                interval=plan['interval'],
                name=plan['name'],
            )
            print("Plan {} created on LIVE".format(plan['id']))
    print("Job done")

if __name__ == '__main__':
    main()
