import {
	staticClasses,
} from "@decky/ui";

import {
	callable,
	definePlugin,
} from "@decky/api"

import { FaFolder } from "react-icons/fa";

import Content from "./views/Content";

const stopUsb = callable<[], void>("stop_usb");

export default definePlugin(() => {
	return {
		name: "MTP",
		title: <div className={staticClasses.Title}>MTP</div>,
		content: <Content />,
		icon: <FaFolder />,
		onDismount() {
			stopUsb();
		},
	};
});
