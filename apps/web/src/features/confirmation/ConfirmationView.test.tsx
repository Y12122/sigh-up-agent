import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ConfirmationView } from "./ConfirmationView";

describe("ConfirmationView", () => {
  it("requires acknowledgement before confirming", async () => {
    const onConfirm = vi.fn();
    render(<ConfirmationView onConfirm={onConfirm} />);

    const button = screen.getByRole("button", { name: /确认注册信息/ });
    expect(button).toBeDisabled();
    await userEvent.click(screen.getByRole("checkbox"));
    await userEvent.click(button);

    expect(onConfirm).toHaveBeenCalledOnce();
  });
});
