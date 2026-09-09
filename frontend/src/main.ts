import { mount } from "svelte";
import "./landing-global.css";
import App from "./AppNew.svelte";

mount(App, { target: document.getElementById("app")! });
