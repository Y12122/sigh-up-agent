import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("renders the employee shell", () => {
    render(<App />);

    expect(screen.getByText("工商注册工作台")).toBeInTheDocument();
  });
});
