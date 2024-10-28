from app.page import Page
from utils import io


def main():
    manifest = io.read_json_file("SumGPT/manifest.json")
    models = io.read_json_file("SumGPT/models.json")

    pg = Page()
    pg.draw_header(manifest["version"])
    pg.draw_sidebar(manifest, models)
    pg.draw_body()


if __name__ == "__main__":
    main()
