import { CheckOutlined } from "@ant-design/icons";
import { Button, Steps, Typography } from "antd";

import { MaterialChecklist } from "./MaterialChecklist";

export function CustomerFlow() {
  return (
    <main className="customer-shell" id="main-content">
      <header className="customer-header">
        <div>
          <Typography.Text type="secondary">案件 HK-20260712-001</Typography.Text>
          <Typography.Title level={2}>恒星贸易有限公司</Typography.Title>
        </div>
        <Typography.Text>资料提交</Typography.Text>
      </header>
      <div className="customer-layout">
        <nav aria-label="资料提交步骤">
          <Steps direction="vertical" current={2} items={[
            { title: "公司信息", icon: <CheckOutlined /> },
            { title: "董事与股东", icon: <CheckOutlined /> },
            { title: "材料上传" },
            { title: "缺件处理" },
            { title: "确认注册信息" }
          ]} />
        </nav>
        <div>
          <MaterialChecklist />
          <div className="flow-actions"><Button type="primary">保存并继续</Button></div>
        </div>
      </div>
    </main>
  );
}

