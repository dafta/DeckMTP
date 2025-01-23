import {
	PanelSectionRow,
	ToggleField,
} from "@decky/ui"

import {
	callable,
} from "@decky/api";

import { useState, useEffect } from "react";

const isRunning = callable<[], boolean>("is_running");
const toggleUsb = callable<[]>("toggle_usb");

export const UsbToggle = () => {
	const [usbStarted, setUsbStarted] = useState<boolean>(false);

	useEffect(() => {
		isRunning().then((running) => {
			setUsbStarted(running);
		});
	}, []);

	return (
		<PanelSectionRow>
			<ToggleField
				label="Start USB Gadgets"
				checked={usbStarted}
				onChange={async () => {
					await toggleUsb()
				}}
			/>
		</PanelSectionRow>
	);
};
