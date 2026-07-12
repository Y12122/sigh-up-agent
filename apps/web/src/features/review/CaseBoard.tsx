import { ClockCircleOutlined, SearchOutlined } from "@ant-design/icons";
import { Input, Table, Tag, Typography } from "antd";

const rows = [
  { id: "HK-20260712-001", company: "恒星贸易有限公司", customer: "陈女士", completeness: "75%", status: "待人工复核", owner: "王审核", age: "18 分钟" },
  { id: "HK-20260712-002", company: "远景顾问有限公司", customer: "李先生", completeness: "50%", status: "待补件", owner: "赵客服", age: "2 小时" },
  { id: "HK-20260711-008", company: "启程科技有限公司", customer: "周女士", completeness: "100%", status: "待客户确认", owner: "王审核", age: "1 天" }
];

export function CaseBoard({ onOpen }: { onOpen: () => void }) {
  return <main className="board" id="main-content">
    <div className="board-heading"><div><Typography.Title level={2}>案件看板</Typography.Title><Typography.Text type="secondary">3 个进行中案件</Typography.Text></div><Input prefix={<SearchOutlined />} placeholder="搜索客户或公司" aria-label="搜索客户或公司" /></div>
    <Table rowKey="id" pagination={false} dataSource={rows} onRow={(record) => ({ onClick: record.id === rows[0].id ? onOpen : undefined })} columns={[
      { title: "案件编号", dataIndex: "id" }, { title: "公司", dataIndex: "company", render: (value, row) => <div><strong>{value}</strong><div className="subtle">{row.customer}</div></div> },
      { title: "材料完整度", dataIndex: "completeness" }, { title: "状态", dataIndex: "status", render: (value) => <Tag color={value === "待补件" ? "error" : "processing"}>{value}</Tag> },
      { title: "负责人", dataIndex: "owner" }, { title: "等待时间", dataIndex: "age", render: (value) => <span><ClockCircleOutlined /> {value}</span> }
    ]} />
  </main>;
}

