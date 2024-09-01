import {
	PanelSection,
	PanelSectionRow,
	ToggleField,
	staticClasses,
} from "@decky/ui";

import {
	callable,
	definePlugin,
} from "@decky/api"

import { useState, useEffect } from "react";
import { FaFolder } from "react-icons/fa";

const is_running = callable<[], boolean>("is_running");
const is_drd_enabled = callable<[], boolean>("is_drd_enabled");
const toggle_gadget = callable<[], boolean>("toggle_gadget");
const stop_gadget = callable<[], void>("stop_gadget");

function Content() {
	const [mtpEnabled, setMtpEnabled] = useState<boolean>(false);
	const [drdEnabled, setDrdEnabled] = useState<boolean>(false);

	useEffect(() => {
		is_drd_enabled().then((enabled) => {
			setDrdEnabled(enabled);
		});
		is_running().then((running) => {
			setMtpEnabled(running);
		});
	}, []);

	return (
		<PanelSection>
			<PanelSectionRow>
				<ToggleField
					label="Enable MTP"
					checked={mtpEnabled}
					disabled={!drdEnabled}
					onChange={async () => {
						await toggle_gadget()
					}}
				/>
			</PanelSectionRow>
			{!drdEnabled && (
				<div>
					<strong>
						<em>DRD is disabled</em>
					</strong>
					<br />
					In order for MTP file transfer to work correctly, DRD
					(Dual-Role Device) must be enabled in the BIOS settings,
					under <em>Advanced</em>, <em>USB Configuration</em>,
					<em>USB Dual-Role Device</em>.
					<br />
					<strong>
						<em>WARNING: USB doesn't work under Windows if DRD is
							enabled. Additionally, booting from USB might not work.
							Disabling DRD will solve these issues, if needed.
						</em>
					</strong>
				</div>
			)}
		</PanelSection>
	);
};

export default definePlugin(() => {
	return {
		name: "MTP",
		title: <div className={staticClasses.Title}>MTP</div>,
		content: <Content />,
		icon: <FaFolder />,
		onDismount() {
			stop_gadget();
		},
	};
});
