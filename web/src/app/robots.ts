import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/dashboard", "/login", "/auth/", "/1/", "/2/", "/3/", "/4/", "/5/", "/6/", "/7/"],
      },
    ],
    sitemap: "https://computare.finance/sitemap.xml",
  };
}