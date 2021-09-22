"""Config flow for DWD::Pollen component.

Used by UI to setup a DWD Pollenflug integration.
"""
import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN
from .DWD import Pollenflug

CONF_REGION_NAME = "region_name"


class DwdPollenflugConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Component config flow."""

    VERSION = 1

    def __init__(self):
        self.pollen = None

    async def async_step_user(self, user_input=None):
        """Handle the start of the config flow.

        Called after integration has been selected in the 'add integration
        UI'. The user_input is set to None in this case. We will open a config
        flow form then.
        This function is also called if the form has been submitted. user_input
        contains a dict with the user entered values then.
        """
        if user_input is None:
            # start of new config flow -> get latest information from DWD
            self.pollen = Pollenflug.Pollenflug()
            await self.hass.async_add_executor_job(self.pollen.fetch)

            data_schema = vol.Schema(
                {
                    vol.Required(CONF_REGION_NAME): vol.In(
                        [
                            self.pollen.regions_list[region_id].name
                            for region_id in self.pollen.regions_with_data
                        ]
                    )
                }
            )

            return self.async_show_form(step_id="user", data_schema=data_schema)

        region_name = user_input[CONF_REGION_NAME]

        region_name_2_id = {
            region.name: region_id
            for (region_id, region) in self.pollen.regions_list.items()
        }

        region_id = region_name_2_id[region_name]

        unique_id = f"{DOMAIN} {region_id}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=region_name, data={"region_id": region_id})
