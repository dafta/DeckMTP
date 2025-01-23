import {
	PanelSectionRow,
	ToggleField,
} from "@decky/ui"

import {
	callable,
} from "@decky/api";

import { useState, useEffect } from "react";

const isFunctionEnabled = callable<[string], boolean>("is_function_enabled");
const toggleFunction = callable<[string]>("toggle_function");

export const EthernetToggle = () => {
	const [ethEnabled, setEthEnabled] = useState<boolean>(false);

	useEffect(() => {
		isFunctionEnabled("ethernet").then((running) => {
			setEthEnabled(running);
		});
	}, []);

	return (
		<PanelSectionRow>
			<ToggleField
				label="Enable Ethernet"
				checked={ethEnabled}
				onChange={async () => {
					await toggleFunction("ethernet")
				}}
			/>
		</PanelSectionRow>
	);
};
