import { ImageResponse } from "next/og";

export const runtime = "edge";

export const alt = "Computare — Open-Source Personal Finance for Canadians";

export const size = {
  width: 1200,
  height: 630,
};

export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#FAFAFA",
          color: "#0A0A0A",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 24,
          }}
        >
          <div
            style={{
              fontSize: 96,
              fontStyle: "italic",
              fontFamily: "serif",
              letterSpacing: "-0.03em",
              lineHeight: 0.95,
            }}
          >
            Computare
          </div>
          <div
            style={{
              width: 120,
              height: 2,
              backgroundColor: "#C9A84C",
            }}
          />
          <div
            style={{
              fontSize: 24,
              color: "#525252",
              textAlign: "center",
              lineHeight: 1.5,
              maxWidth: 600,
            }}
          >
            Open-source personal finance for Canadians.
            <br />
            Import statements. Categorize with AI. Own your data.
          </div>
          <div
            style={{
              marginTop: 16,
              fontSize: 16,
              color: "#A3A3A3",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
            }}
          >
            Scotiabank &bull; Wealthsimple &bull; American Express
          </div>
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}