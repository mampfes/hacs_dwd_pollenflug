"""Config flow for DWD::Pollen component.

Used by UI to setup a DWD Pollenflug integration.
"""
import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_REGION_ID, DOMAIN
from .DWD import Pollenflug

CONF_REGION_NAME = "region_name"


class DwdPollenflugConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Component config flow."""

    VERSION = 1

    def __init__(self):
        self._source = None

    async def async_step_user(self, user_input=None):
        """Handle the start of the config flow.

        Called after integration has been selected in the 'add integration
        UI'. The user_input is set to None in this case. We will open a config
        flow form then.
        This function is also called if the form has been submitted. user_input
        contains a dict with the user entered values then.
        """
        if self._source is None:
            # start of new config flow -> get latest information from DWD
            self._source = Pollenflug.Pollenflug()

            try:
                await self.hass.async_add_executor_job(self._source.fetch)
            except Exception:
                return self.async_abort(reason="fetch_failed")

        # query top level regions
        data_schema = vol.Schema(
            {
                vol.Required(CONF_REGION_NAME): vol.In(
                    sorted(
                        [
                            region.name
                            for region in self._source.regions_list.values()
                            if region.parent_id is None
                        ]
                    )
                )
            }
        )

        return self.async_show_form(step_id="region", data_schema=data_schema)

    async def async_step_region(self, user_input=None):
        region_name = user_input[CONF_REGION_NAME]

        region_name_2_id = {
            region.name: region_id
            for (region_id, region) in self._source.regions_list.items()
        }

        region_id = region_name_2_id[region_name]

        if region_id not in self._source.regions_with_data:
            # this region has no data => search again in sub-regions
            data_schema = vol.Schema(
                {
                    vol.Required(CONF_REGION_NAME): vol.In(
                        sorted(
                            [
                                region.name
                                for region in self._source.regions_list.values()
                                if region.parent_id == region_id
                            ]
                        )
                    )
                }
            )

            return self.async_show_form(step_id="subregion", data_schema=data_schema)

        else:
            # this region has data => create an entry for this region
            unique_id = f"{DOMAIN} {region_id}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=region_name, data={CONF_REGION_ID: region_id}
            )

    async def async_step_subregion(self, user_input=None):
        return await self.async_step_region(user_input)
