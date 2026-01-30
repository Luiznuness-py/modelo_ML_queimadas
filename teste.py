from source.carregar_dados import carregar_dados


from source.core.settings import Settings


if __name__ == '__main__':
    settings = Settings()

    carregar_dados(settings=settings)