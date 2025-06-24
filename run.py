import time
time_a = time.time()
import uvicorn
from uvicorn.lifespan.on import LifespanOn
import click
import sys

# from tools.locate_print import locate_print
# locate_print("'udadmin:user'")


class UdLifespanOn(LifespanOn):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def startup(self) -> None:
        await super().startup()

        # ud add
        addr = click.style(
            f"http://{self.config.host}:{self.config.port}",
            bold=True,
            # fg=(255, 12, 128),
            fg=(97, 175, 254),
        )
        self.logger.info(f"Server running on {addr} (Press CTRL+C to quit)")
        time_b = time.time()
        spend = click.style(f"{time_b - time_a:.6f}", bold=True, fg=(255, 0, 255))
        self.logger.info(f"sever startup in {spend} seconds.")


sys.modules["uvicorn.lifespan.on"].LifespanOn = UdLifespanOn

# 启动应用
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=3014, reload=True)
    # uvicorn.run("main:app", host="localhost", port=3014)
    # uvicorn.run("main:app", host="localhost", port=1008)
    
