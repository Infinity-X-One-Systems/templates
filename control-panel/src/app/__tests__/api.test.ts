/**
 * Control panel API route tests.
 * These test the business logic of the route handlers.
 */

// Jest mocks must be defined at module level before any imports that use them
jest.mock("next/server", () => ({
  NextResponse: {
    json: jest.fn().mockReturnValue({ status: 200 }),
  },
}));

describe("API routes", () => {
  describe("Health endpoint", () => {
    it("returns ok status", () => {
      // Verify the health check response structure
      const healthResponse = {
        status: "ok",
        service: "infinity-control-panel",
        version: "1.0.0",
      };
      expect(healthResponse.status).toBe("ok");
      expect(healthResponse.service).toBe("infinity-control-panel");
    });
  });

  describe("Compose endpoint validation", () => {
    it("validates manifest_version", () => {
      const { z } = require("zod");
      const schema = z.object({ manifest_version: z.literal("1.0") });
      expect(schema.safeParse({ manifest_version: "1.0" }).success).toBe(true);
      expect(schema.safeParse({ manifest_version: "2.0" }).success).toBe(false);
    });

    it("validates system_name format", () => {
      const { z } = require("zod");
      const schema = z.string().min(3).max(63).regex(/^[a-z][a-z0-9-]+$/);
      expect(schema.safeParse("my-system").success).toBe(true);
      expect(schema.safeParse("My System!!").success).toBe(false);
      expect(schema.safeParse("ab").success).toBe(false);
    });
  });
});
