import {
  definePlugin,
  PanelSection,
  PanelSectionRow,
  ToggleField,
  ServerAPI,
  staticClasses,
} from "decky-frontend-lib";
import { useState, useEffect, VFC } from "react";
import { FaShip } from "react-icons/fa";

import * as backend from "./backend";

const Content: VFC<{ serverAPI: ServerAPI }> = ({}) => {
  const [mtpEnabled, setMtpEnabled] = useState<boolean>(false);

  useEffect(() => {
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
        />
      </PanelSectionRow>
    </PanelSection>
  );
};

export default definePlugin((serverApi: ServerAPI) => {
  backend.setServerAPI(serverApi);

  return {
    title: <div className={staticClasses.Title}>MTP</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <FaShip />,
    onDismount() {
    },
  };
});
