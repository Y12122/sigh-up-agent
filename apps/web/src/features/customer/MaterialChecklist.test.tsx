import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { MaterialChecklist } from "./MaterialChecklist";

describe("MaterialChecklist", () => {
  it("shows missing materials and uploads against the selected role", async () => {
    const onUpload = vi.fn();
    const { container } = render(<MaterialChecklist onUpload={onUpload} />);

    expect(screen.getByText("还需补交 2 项")).toBeVisible();
    const file = new File(["%PDF-1.7 synthetic"], "address-proof.pdf", {
      type: "application/pdf"
    });
    const input = container.querySelector<HTMLInputElement>('input[type="file"][accept*=".pdf"]');
    expect(input).not.toBeNull();
    await userEvent.upload(input!, file);

    expect(onUpload).toHaveBeenCalledWith(
      expect.objectContaining({ file, materialType: "address_proof", personRole: "director" })
    );
  });
});
