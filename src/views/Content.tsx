import {
	PanelSection,
} from "@decky/ui";

import {
	callable,
} from "@decky/api";

import { useState, useEffect } from "react";

import { DrdWarning } from "../components/DrdWarning"
import { UsbToggle } from "../components/UsbToggle"
import { MtpToggle } from "../components/MtpToggle"
import { EthernetToggle } from "../components/EthernetToggle"

const isDrdEnabled = callable<[], boolean>("is_drd_enabled");

function Content() {
	const [drdEnabled, setDrdEnabled] = useState<boolean>(false);

	useEffect(() => {
		isDrdEnabled().then((enabled) => {
			setDrdEnabled(enabled);
		});
	}, []);

	if (drdEnabled == false) {
		return (
			<DrdWarning />
		);
	};

	return (
		<PanelSection>
			<PanelSection>
				<UsbToggle />
			</PanelSection>
			<PanelSection>
				<strong>
					USB Gadgets:
				</strong>
				<MtpToggle />
				<EthernetToggle />
			</PanelSection>
		</PanelSection>
	);
};

export default Content;
