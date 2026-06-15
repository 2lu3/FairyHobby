class Store(Base, table=True):
    __tablename__ = "stores"

    name: str
    description: str
    image_url: str

    address: str | None
    latitude: float | None
    longitude: float | None
