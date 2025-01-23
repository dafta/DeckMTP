import {
	PanelSectionRow,
	ToggleField,
} from "@decky/ui"

import {
	callable,
} from "@decky/api";

import { useState, useEffect } from "react";

const isFunctionEnabled = callable<[string], boolean>("is_function_enabled");
const toggleFunction = callable<[string], boolean>("toggle_function");

export const MtpToggle = () => {
	const [mtpEnabled, setMtpEnabled] = useState<boolean>(false);

	useEffect(() => {
		isFunctionEnabled("mtp").then((running) => {
			setMtpEnabled(running);
		});
	}, []);

	return (
		<PanelSectionRow>
			<ToggleField
				label="Enable MTP"
				checked={mtpEnabled}
				onChange={async () => {
					await toggleFunction("mtp")
				}}
			/>
		</PanelSectionRow>
	);
};
