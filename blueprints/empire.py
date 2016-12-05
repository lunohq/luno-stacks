from stacker_blueprints.empire.controller import EmpireController
from stacker_blueprints.empire.minion import EmpireMinion


class Base(object):

    def get_local_parameters(self):
        params = getattr(self, "LOCAL_PARAMETERS", {})
        params.update({
            "DataDogAPIKey": {
                "type": str,
                "description": "API key for Data Dog",
            },
            "DataDogTags": {
                "type": str,
                "description": "Tags to include for Data Dog",
            },
        })
        setattr(self, "LOCAL_PARAMETERS", params)
        return super(Base, self).get_local_parameters()

    def generate_seed_contents(self):
        seed = super(Base, self).generate_seed_contents()
        api_key = self.local_parameters["DataDogAPIKey"]
        tags = self.local_parameters.get("DataDogTags")
        if api_key:
            seed.append("EMPIRE_DATA_DOG_API_KEY={}\n".format(api_key))

        if tags:
            seed.append("EMPIRE_DATA_DOG_TAGS={}\n".format(tags))

        return seed


class Controller(Base, EmpireController):
    pass


class Minion(Base, EmpireMinion):
    pass
