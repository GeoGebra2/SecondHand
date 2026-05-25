from app.schemas.common import OverviewCard


class DashboardService:
    def get_dashboard_cards(self) -> list[OverviewCard]:
        return [
            OverviewCard(label='今日新增商品', value='18', description='待审核和已上架商品总数'),
            OverviewCard(label='活跃订单', value='7', description='正在交易中的订单数量'),
            OverviewCard(label='异常预警', value='2', description='待进一步核查的异常行为记录'),
        ]


service = DashboardService()
