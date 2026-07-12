import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { ReviewWorkbench } from "./ReviewWorkbench";

describe("ReviewWorkbench", () => {
  it("keeps source document beside the selected risky field", async () => {
    render(<ReviewWorkbench />);

    await userEvent.click(screen.getByRole("button", { name: "复核证件号" }));

    expect(screen.getByLabelText("材料预览")).toHaveAttribute("data-page", "1");
    expect(screen.getByText("OCR 置信度 72%")).toBeVisible();
  });
});
