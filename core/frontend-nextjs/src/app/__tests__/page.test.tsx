import { render, screen } from "@testing-library/react";
import HomePage from "../page";

// Mock next/link since we're in a test environment
jest.mock("next/link", () => ({ __esModule: true, default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a> }));

describe("HomePage", () => {
  it("renders heading", () => {
    render(<HomePage />);
    expect(screen.getByText("Infinity X One")).toBeInTheDocument();
  });

  it("renders navigation links", () => {
    render(<HomePage />);
    expect(screen.getByText("Open Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Documentation")).toBeInTheDocument();
  });
});
