import {
  definePlugin,
  PanelSection,
  PanelSectionRow,
  ToggleField,
  ServerAPI,
  staticClasses,
} from "decky-frontend-lib";
import { useState, useEffect, VFC } from "react";
import { FaFolder } from "react-icons/fa";

import * as backend from "./backend";

const Content: VFC<{ serverAPI: ServerAPI }> = ({}) => {
  const [mtpEnabled, setMtpEnabled] = useState<boolean>(false);
  const [drdEnabled, setDrdEnabled] = useState<boolean>(false);

  useEffect(() => {
    backend.is_drd_enabled().then((enabled) => {
      setDrdEnabled(enabled);
    });
    backend.is_running().then((running) => {
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
            await backend.toggle_mtp()
          }}
        />
      </PanelSectionRow>
      {!drdEnabled && (
        <div>
          <strong>
            <em>DRD is disabled</em>
          </strong>
          <br/>
          In order for MTP file transfer to work correctly, DRD
          (Dual-Role Device) must be enabled in the BIOS settings,
          under <em>Advanced</em>, <em>USB Configuration</em>,
          <em>USB Dual-Role Device</em>.
          <br/>
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

export default definePlugin((serverApi: ServerAPI) => {
  backend.setServerAPI(serverApi);

  return {
    title: <div className={staticClasses.Title}>MTP</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <FaFolder />,
    onDismount() {
      backend.stop_mtp()
    },
  };
});
