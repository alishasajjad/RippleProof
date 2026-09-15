import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "RippleProof",
    short_name: "RippleProof",

    description:
      "Semantic policy change intelligence with executable proof.",

    start_url: "/",

    display: "standalone",

    background_color: "#020e1a",

    theme_color: "#061827",

    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
      },
    ],
  };
}