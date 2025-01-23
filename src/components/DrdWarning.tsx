import {
	PanelSection,
	PanelSectionRow,
} from "@decky/ui";

export const DrdWarning = () => {

	return (
		<PanelSection>
			<PanelSectionRow>
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
			</PanelSectionRow>
		</PanelSection>
	)
}
