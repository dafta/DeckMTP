import {
  ServerAPI
} from "decky-frontend-lib"

var serverAPI: ServerAPI | undefined = undefined;

export function setServerAPI(s: ServerAPI) {
  serverAPI = s;
}

async function backend_call<I, O>(name: string, params: I): Promise<O> {
  try {
    const res = await serverAPI!.callPluginMethod<I, O>(name, params);
    if (res.success) return res.result;
    else {
      console.error(res.result);
      throw res.result;
    }
  } catch (e) {
    console.error(e);
    throw e;
  }
}

export async function is_running(): Promise<boolean> {
  return backend_call<{}, boolean>("is_running", {});
}

export async function is_drd_enabled(): Promise<boolean> {
  return backend_call<{}, boolean>("is_drd_enabled", {});
}

export async function toggle_gadget(): Promise<boolean> {
  return backend_call<{}, boolean>("toggle_gadget", {});
}

export async function stop_gadget(): Promise<{}> {
  return backend_call<{}, {}>("stop_gadget", {});
}
